# 🧠 ATS Analyzer GPT

🚀 مشروع ذكاء اصطناعي لتحليل السير الذاتية وجعلها متوافقة مع أنظمة تتبع المتقدمين (ATS) باستخدام OpenAI + FastAPI.  
يساعدك على تقييم ملفك الشخصي والحصول على سكور احترافي يعكس مدى توافقه مع فرص العمل.

---

## ✅ الميزات

- 🔍 استخراج النصوص من ملفات PDF و DOCX
- 🤖 تحليل الكلمات المفتاحية باستخدام GPT
- 📊 حساب درجة ATS بطريقة ذكية (بدون مقارنة حرفية فقط)
- ⚙️ مبني باستخدام **FastAPI** وواجهة **Swagger UI**
- 🔐 تم فصل مفاتيح API بطريقة آمنة باستخدام `.env`

---

## 📷 لقطة من الواجهة

![screenshot](https://user-images.githubusercontent.com/AbdellaAnalytics/ats-analyzer-gpt/screenshot.png)  
*(اضف صورة من الواجهة لو حبيت)*

---

## 🧰 التثبيت والتشغيل

```bash
git clone https://github.com/AbdellaAnalytics/ats-analyzer-gpt.git
cd ats-analyzer-gpt
pip install -r requirements.txt
uvicorn main:app --reload
