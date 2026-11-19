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
- Kompyuterda birinchi ishga tushirish uchun standart login: `malika`, parol: `Malika2026!`.
- Render’da Environment bo‘limida `ADMIN_PASSWORD` uchun albatta o‘zingizning kuchli parolingizni kiriting. Birinchi kirgandan keyin admin panelda ham parolni almashtiring.

## Render
GitHub repositoryga barcha fayllarni yuklang. Render’da New > Blueprint tanlab repositoryni ulang. `ADMIN_PASSWORD` qiymatini Render Environment’da o‘zingiz belgilagan kuchli parol bilan kiriting. Rasmlar `/var/data/uploads` papkasida saqlanadi va persistent diskda qoladi. `render.yaml` persistent diskni `/var/data` ga ulaydi.


## Admin orqali sayt dizayn kodini tahrirlash
Admin panelga kirib, yuqoridagi “Sayt kodini tahrirlash” bo‘limini oching yoki /admin/code manziliga kiring. Hozircha index.html va style.css tahrirlanadi. Har saqlashdan oldin zaxira nusxa olinadi; “Asl kodni tiklash” orqali standart holatga qaytish mumkin. app.py kabi Python server kodi ataylab paneldan tahrirlanmaydi.
