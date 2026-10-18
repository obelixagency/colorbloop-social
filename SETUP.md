# Colorbloop — أوتوميشن انستجرام وفيسبوك

نفس محرك Unshaken: GitHub Actions بيشتغل كل نص ساعة، وبينشر اللي ميعاده جه من `calendar.json`، وبيعيد أي حاجة فشلت. ولو بوست اتأخر أكتر من ساعتين ونص، GitHub بيبعتلك إيميل.

## اللي جوه الريبو
| ملف | وظيفته |
|---|---|
| `calendar.json` | الجدول: بوستات البراند بتواريخ ثابتة، وخطة لكل كتاب بتبدأ من يوم نزوله (بتوقيت أمريكا الشرقي ET) |
| `assets/` | كل الصور والفيديوهات جاهزة (الريلز معمولة بموسيقى مولّدة بالكود، فمفيش حقوق) |
| `links.json` | لينكات الكتب على أمازون وEtsy. **البوست اللي محتاج لينك كتاب مش بينزل غير لما تحط اللينك.** |
| `build_site.py` | صفحة Link-in-bio احتياطي لو عملنا موقع بعدين (مش مستخدمة دلوقتي) |
| `watchdog.py` + `publish.py` | النشر، والكود متاخد من Unshaken |
| `sim_watchdog.py` | محاكاة 60 يوم من غير نشر حقيقي، للتأكد إن مفيش زحمة. شغّلها بـ `python sim_watchdog.py` |

## 1) الحسابات
- صفحة فيسبوك اسمها **Colorbloop**، وحساب انستجرام **@color.bloop** يكون **Business** أو **Creator** ومربوط بالصفحة (من Accounts Center).
- في **Meta for Developers** تقدر تستخدم نفس الـ App بتاع Unshaken، أو تعمل App جديد اسمه "Colorbloop Automation" في Business Portfolio خاص بـ Colorbloop.
  الصلاحيات المطلوبة: `pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish`
- خطوات الـ **Page Token** الدائم هي نفسها اللي عملناها في Unshaken: Graph API Explorer، وبعدها long-lived user token، وبعدها `/me/accounts` تاخد منه توكن الصفحة.
- `IG_USER_ID` بتجيبه من: `GET /{page-id}?fields=instagram_business_account`

## 2) الريبو (✅ اتعمل)
`obelixagency/colorbloop-social` **Public**، و GitHub Pages شغال على `main`. الصور بتطلع من هنا، ومفيش أي سر محفوظ في الملفات.

## 3) الـ Secrets (المتبقي الوحيد)
Settings ← Secrets and variables ← Actions ← New repository secret:
| Secret | القيمة |
|---|---|
| `FB_PAGE_ID` | `1418685554653190` (صفحة Colorbloop) |
| `IG_USER_ID` | `17841473038668312` (@color.bloop) |
| `FB_PAGE_TOKEN` | Page token دائم لصفحة Colorbloop، وبيتعمل بنفس خطوات Unshaken |

**يوتيوب (✅ متوصل):** مشروع Google Cloud اسمه `colorbloop-automation` (حالته Production)، وفيه 4 أسرار: `YT_CLIENT_ID` و`YT_CLIENT_SECRET` و`YT_REFRESH_TOKEN` و`YT_CHANNEL_ID` (`UC12ArjNzd_Jdbn5_I-_ZYVQ`). أي ريل بيتنشر بينزل كمان Short على @Colorbloopbooks.
**فحص الاتصال:** من Actions ← Check Meta connection ← Run workflow. الفحص ده ما بينشرش أي حاجة.

## 4) البايو (من غير موقع)
- مفيش موقع ومفيش أي لينك github.io قدام الناس. ريبو `colorbloop-media` بيشيل الصور بس، لأن API انستجرام محتاج لينك عام للصورة، والعنوان ده ما بيظهرش لحد.
- **لينك البايو في انستجرام** = لينك أمازون لأول كتاب يتقبل. وبعد Author Central نغيّره لصفحة المؤلف على أمازون (`amazon.com/author/...`)، اللي فيها كل الكتب.
- **فيسبوك:** كل بوست بيبقى فيه لينك أمازون المباشر للكتاب.

**الحسابات:** انستجرام وفيسبوك `@color.bloop` · يوتيوب `@Colorbloopbooks`

## 5) التشغيل
تاب **Actions** ← "Colorbloop watchdog" ← **Run workflow** مرة للتجربة. بعد كده هيشتغل لوحده.

## الإطلاق أوتوماتيك
**مفيش أي حاجة هتتنشر قبل ما الكتب تتقبل.** أول ما تحط أول لينك أمازون في `links.json`، اليوم ده بيبقى يوم الإطلاق، وبوستات البراند (التعريف، Meet Bloop، التيبس، before/after، و4 ريلز براند) بتمشي على جدولها من اليوم ده.

## كل كتاب ليه جدوله الخاص (جديد)
الكتب بتنزل على أمازون واحد ورا التاني (حوالي كتابين في الأسبوع)، فكل كتاب بقى ليه خطة بتبدأ **من يوم ما تحط لينكه**:
| اليوم | المحتوى |
|---|---|
| 0 | ستوري الإطلاق 6:00 م + ريل الإطلاق 7:30 م |
| 2 | كاروسيل 10:00 ص |
| 4 و 6 | ستوري "Peek inside" 6:00 م |
| 9 | ريل Flip-through (بنقلب صفحات الكتاب) 7:30 م |
| 16 | ريل "Watch it get colored" (صفحة بتتلوّن قدامك) 7:30 م |

(الكتب الـ 7 الأولانية محتفظة بنفس ترتيبها القديم، واتزود لها ريلز يوم 9 ويوم 16.)

- أول تشغيل بعد ما تحط اللينك بيسجّل في `publish_log.json` حاجة اسمها `_live_<الكتاب>`. لو اللينك اتحط بعد ميعاد أول بوست في يوم 0، الخطة بتبدأ من بكرة، علشان مفيش بوست يتنشر متأخر.
- **مفيش زحمة:** ريل واحد بس في اليوم، وبوست/كاروسيل واحد في اليوم، وستوري واحدة في كل ميعاد. لو كتابين نزلوا في نفس اليوم، أو حصل تعارض، البوست بيتأجل يوم. الأولوية لبوستات الإطلاق، وبعدها الـ Peeks، وبعدها الريلز الإضافية. وأي حاجة اتنشرت خلاص مكانها مش بيتغير.
- لو حاجة اتأخرت (مثلاً Actions وقف كام ساعة)، بينزل بوست متأخر واحد بس من كل نوع في كل تشغيل، يعني مفيش طوفان بوستات.

## لما كتاب ينزل
تحط لينكه في `links.json` (مثلاً `"dinosaurs": "https://www.amazon.com/dp/XXXX"`) وتعمل Commit. بعدها:
- خطة الكتاب ده هتبدأ لوحدها، وأول حاجة ستوري وريل الإطلاق.
- كابشن فيسبوك ويوتيوب هيبقى فيه اللينك المباشر، وكابشن انستجرام هيقول "link in bio".
- الكتب: `xmas_activity, abc, xmas_coloring, thanksgiving, numbers, shapes, preschool, animals, kindergarten, dinosaurs, vehicles, unicorns, scissors, sightwords, handwriting, cursive, space, feelings, valentines, easter`

ملحوظة: API انستجرام مش بيسمح بستيكر اللينك في الستوري، وده قيد من Meta نفسها. علشان كده الستوريز بتقول "Tap the link in our bio".
