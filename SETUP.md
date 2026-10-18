# Colorbloop — أوتوميشن انستجرام وفيسبوك

نفس محرك Unshaken: GitHub Actions بيشتغل كل نص ساعة، وبينشر اللي ميعاده جه من `calendar.json`، وبيعيد أي حاجة فشلت. ولو بوست اتأخر أكتر من ساعتين ونص، GitHub بيبعتلك إيميل.

## اللي جوه الريبو
| ملف | وظيفته |
|---|---|
| `calendar.json` | جدول 30 يوم: بوستات وكاروسيل وستوريز وريلز، بتوقيت أمريكا الشرقي (ET) |
| `assets/` | كل الصور والفيديوهات جاهزة (الريلز معمولة بموسيقى مولّدة بالكود، فمفيش حقوق) |
| `links.json` | لينكات الكتب على أمازون وEtsy. **البوست اللي محتاج لينك كتاب مش بينزل غير لما تحط اللينك.** |
| `build_site.py` | صفحة Link-in-bio احتياطي لو عملنا موقع بعدين (مش مستخدمة دلوقتي) |
| `watchdog.py` + `publish.py` | النشر، والكود متاخد من Unshaken |

## 1) الحسابات
- صفحة فيسبوك اسمها **Colorbloop**، وحساب انستجرام **@color.bloop** يكون **Business** أو **Creator** ومربوط بالصفحة (من Accounts Center).
- في **Meta for Developers** تقدر تستخدم نفس الـ App بتاع Unshaken، أو تعمل App جديد اسمه "Colorbloop Automation" في Business Portfolio خاص بـ Colorbloop.
  الصلاحيات المطلوبة: `pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish`
- خطوات الـ **Page Token** الدائم هي نفسها اللي عملناها في Unshaken: Graph API Explorer، وبعدها long-lived user token، وبعدها `/me/accounts` تاخد منه توكن الصفحة.
- `IG_USER_ID` بتجيبه من: `GET /{page-id}?fields=instagram_business_account`

## 2) الريبوهين (على obelixagency)
1. `colorbloop-social`: **Private**، وده فيه الملفات دي كلها.
2. `colorbloop-media`: **Public**، وفاضي. فعّل فيه **GitHub Pages** من Settings، ثم Pages، ثم Branch: `main` / root.

## 3) الـ Secrets في colorbloop-social
Settings ← Secrets and variables ← Actions ← New repository secret:
| Secret | القيمة |
|---|---|
| `FB_PAGE_ID` | ID صفحة Colorbloop |
| `FB_PAGE_TOKEN` | Page token الدائم |
| `IG_USER_ID` | ID حساب انستجرام البيزنس |
| `MEDIA_REPO_TOKEN` | Personal access token فيه صلاحية `contents:write` على `colorbloop-media`، وينفع تستخدم نفس توكن Unshaken لو بيغطي الريبو الجديد |

## 4) البايو (من غير موقع)
- مفيش موقع ومفيش أي لينك github.io قدام الناس. ريبو `colorbloop-media` بيشيل الصور بس، لأن API انستجرام محتاج لينك عام للصورة، والعنوان ده ما بيظهرش لحد.
- **لينك البايو في انستجرام** = لينك أمازون لأول كتاب يتقبل. وبعد Author Central نغيّره لصفحة المؤلف على أمازون (`amazon.com/author/...`)، اللي فيها كل الكتب.
- **فيسبوك:** كل بوست بيبقى فيه لينك أمازون المباشر للكتاب.

**الحسابات:** انستجرام وفيسبوك `@color.bloop` · يوتيوب `@Colorbloopbooks`

## 5) التشغيل
تاب **Actions** ← "Colorbloop watchdog" ← **Run workflow** مرة للتجربة. بعد كده هيشتغل لوحده.

## الإطلاق أوتوماتيك
**مفيش أي حاجة هتتنشر قبل ما الكتب تتقبل.** أول ما تحط أول لينك أمازون في `links.json`، اليوم ده بيبقى يوم الإطلاق، والجدول بتاع الـ 4 أسابيع بيبدأ منه لوحده. يعني بوست التعريف بيتنشر الساعة 10 الصبح بتوقيت أمريكا، والباقي بعده بالترتيب.

## لما كتاب ينزل
تحط لينكه في `links.json` (مثلاً `"abc": "https://www.amazon.com/dp/XXXX"`) وتعمل Commit. بعدها:
- البوستات والريلز الخاصة بالكتاب ده هتنزل في أقرب ميعاد ليها.
- كابشن فيسبوك هيبقى فيه اللينك المباشر، وكابشن انستجرام هيقول "link in bio".

ملحوظة: API انستجرام مش بيسمح بستيكر اللينك في الستوري، وده قيد من Meta نفسها. علشان كده الستوريز بتقول "Tap the link in our bio".
