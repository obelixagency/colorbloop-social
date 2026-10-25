"""Offline tests: no real credentials or social network calls."""
import contextlib, io, json, os, runpy, unittest
from unittest.mock import patch, Mock
import publish as P
import watchdog as W

class TokenSafety(unittest.TestCase):
    def test_exception_never_persisted(self):
        secret='synthetic-refresh-token-DO-NOT-LOG'
        with patch.dict(P.DISPATCH, {'test': Mock(side_effect=RuntimeError('https://api.invalid/?access_token='+secret))}):
            ok, detail=P.publish('test', '', '')
        self.assertFalse(ok)
        self.assertNotIn(secret, json.dumps(detail))
    def test_api_error_retains_auth_signal_not_body(self):
        r=Mock(status_code=400);r.json.return_value={'error': {'code':190,'type':'OAuthException','message':'synthetic-token'}}
        with self.assertRaises(P.APIError) as e:P._check(r)
        with patch.dict(P.DISPATCH, {'test':Mock(side_effect=e.exception)}):
            ok, detail=P.publish('test','','')
        self.assertTrue(W._auth_dead(detail));self.assertNotIn('synthetic-token',json.dumps(detail))
    def test_non_json_body_withheld(self):
        r=Mock(status_code=500,text='synthetic-token');r.json.side_effect=ValueError('synthetic-token')
        with self.assertRaises(P.APIError) as e:P._check(r)
        self.assertNotIn('synthetic-token',str(e.exception))
    def test_success_response_allowlist(self):
        ref={'id':'12345','access_token':'synthetic-token','upload_url':'https://private.invalid','ntfy_topic':'private'}
        with patch.dict(P.DISPATCH, {'test':Mock(return_value=ref)}):
            self.assertEqual(P.publish('test','',''),(True,{'platform_ref':{'id':'12345'}}))
    def test_fallback_stdout_withholds_exception(self):
        with patch.object(P,'_fb_page',return_value=('page','token')), patch.object(P,'_fb_rupload',side_effect=RuntimeError('synthetic-token')), patch('builtins.open', side_effect=FileNotFoundError), contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(FileNotFoundError):P.publish_facebook_reel('missing','')
        self.assertNotIn('synthetic-token',out.getvalue())
    def test_connection_transport_failure_withheld(self):
        with patch.dict(os.environ, {'FB_PAGE_TOKEN':'synthetic-token','FB_PAGE_ID':'page','IG_USER_ID':'ig'}), patch('requests.get',side_effect=RuntimeError('synthetic-token')), contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as e:runpy.run_path('check_tokens.py',run_name='__main__')
        self.assertEqual(e.exception.code,1);self.assertNotIn('synthetic-token',out.getvalue())

if __name__=='__main__':unittest.main()
