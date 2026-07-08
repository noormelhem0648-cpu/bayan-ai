# 🚀 دليل نشر Bayan AI على الإنترنت (خطوة بخطوة)

المشروع جاهز 100% للنشر. تحتاجين فقط لحسابين مجانيين: **GitHub** و **Render**.
كل شيء آلي عبر ملف `render.yaml` — لن تكتبي أي كود.

الوقت المتوقع: 10–15 دقيقة.

---

## الخطوة 1 — أنشئي حساب GitHub ومستودعاً فارغاً
1. افتحي https://github.com وأنشئي حساباً (مجاني).
2. اضغطي **New repository** (زر أخضر).
3. الاسم: `bayan-ai` — اتركيه **Public** — **لا** تضيفي README.
4. اضغطي **Create repository**. ستظهر صفحة فيها رابط المستودع، مثل:
   `https://github.com/USERNAME/bayan-ai.git`

## الخطوة 2 — ارفعي المشروع إلى GitHub
افتحي **PowerShell** والصقي هذه الأوامر (غيّري `USERNAME` باسمك):

```powershell
cd "C:\Users\User\OneDrive\Desktop\AL Bayan AI"
git remote add origin https://github.com/USERNAME/bayan-ai.git
git push -u origin main
```

عند أول `push` ستفتح نافذة متصفح لتسجيل الدخول إلى GitHub — سجّلي الدخول واسمحي.
> إن قال إن `origin` موجود مسبقاً، استخدمي:
> `git remote set-url origin https://github.com/USERNAME/bayan-ai.git`

## الخطوة 3 — انشري كل شيء على Render بضغطة واحدة
1. افتحي https://render.com وسجّلي الدخول بـ **GitHub** (الأسهل).
2. اضغطي **New +** → **Blueprint**.
3. اختاري مستودع `bayan-ai`.
4. سيقرأ Render ملف `render.yaml` تلقائياً ويجهّز 3 خدمات:
   - قاعدة بيانات PostgreSQL
   - الخادم (backend)
   - الواجهة (frontend)
5. سيطلب منك قيمة **GEMINI_API_KEYS** → الصقي مفتاح Gemini الخاص بك
   (احصلي عليه من https://aistudio.google.com/apikey — يبدأ بـ `AIza`).
6. اضغطي **Apply**. انتظري 5–10 دقائق حتى يكتمل البناء.

## الخطوة 4 — جاهز! 🎉
بعد اكتمال النشر، افتحي خدمة **bayan-ai-frontend** في Render — ستجدين رابطاً مثل:
```
https://bayan-ai-frontend.onrender.com
```
هذا هو رابط موقعك على الإنترنت. شاركيه مع من تشائين.

**تسجيل الدخول الأول كمدير:**
البريد: `admin@bayan.ai` — كلمة المرور: `Admin@12345`
(غيّري كلمة المرور فوراً من صفحة الملف الشخصي.)

---

## ملاحظات على الخطة المجانية
- الخادم المجاني "ينام" بعد 15 دقيقة من عدم الاستخدام، ويستيقظ خلال ~30 ثانية عند أول
  زيارة (طبيعي).
- قاعدة البيانات المجانية على Render صالحة 30 يوماً — للاستخدام الدائم رقّيها لخطة مدفوعة.
- فهارس الكتب (FAISS) مؤقتة على الخطة المجانية؛ أعيدي بناء الفهرس من لوحة المدرّس بعد أي
  إعادة تشغيل. للثبات الدائم: رقّي الخادم وأضيفي قرصاً دائماً (مشروح داخل `render.yaml`).

## طريقة بديلة للواجهة فقط (Vercel)
يمكن نشر الواجهة على Vercel بدلاً من Render:
1. https://vercel.com → **Import** مستودع GitHub → اختاري مجلد `frontend`.
2. أضيفي متغيّر البيئة `VITE_API_BASE_URL` = رابط الخادم على Render + `/api/v1`.
3. Deploy.
```
