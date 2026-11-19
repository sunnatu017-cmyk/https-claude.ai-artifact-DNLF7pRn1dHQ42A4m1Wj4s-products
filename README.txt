# Malika Herbalife — Flask sayt

## Kompyuterda ishga tushirish
1. Python 3.10+ o‘rnating.
2. Terminalda loyiha papkasiga kiring.
3. `python -m venv venv`
4. Windows: `venv\\Scripts\\activate` (Mac/Linux: `source venv/bin/activate`)
5. `pip install -r requirements.txt`
6. `python app.py`
7. Brauzerda http://127.0.0.1:5000 oching.

## Admin
- Manzil: `/login`
- Boshlang‘ich login: `malika`
- Boshlang‘ich parol: `Malika2026!`
- Birinchi kirgandan keyin Admin paneldagi “Admin parolini almashtirish” bo‘limidan parolni almashtiring.

## Render
GitHub repositoryga barcha fayllarni yuklang. Render’da New > Blueprint tanlab repositoryni ulang. `ADMIN_PASSWORD` qiymatini Render Environment’da o‘zingiz belgilagan kuchli parol bilan kiriting. `render.yaml` persistent diskni `/var/data` ga ulaydi.
