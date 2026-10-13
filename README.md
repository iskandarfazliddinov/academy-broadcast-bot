# 🎓 Akademiya Reklama va Yangiliklar Tarqatuvchi Telegram Boti

Ushbu bot akademiya, o'quv markazi yoki har qanday tashkilotning reklama roliklari, yangiliklari va postlarini o'ziga ulangan barcha Telegram guruhlari va kanallariga bir vaqtning o'zida avtomatik tarzda tarqatish (broadcast) uchun mo'ljallangan.

---

## ✨ Imkoniyatlari

1. **Avtomatik aniqlash va saqlash:**
   - Bot yangi kanalga (Admin sifatida) yoki guruhga qo'shilishi bilanoq, chat ma'lumotlarini (nomi, ID si, username, turi) SQLite ma'lumotlar bazasiga avtomatik yozib oladi.
   - Bot chiqarib yuborilganda yoki huquqlari cheklanganda, ushbu chat avtomatik tarzda nofaol deb belgilanadi.
   - Har bir yangi kanal/guruh qo'shilganda bot adminlarga bildirishnoma yuboradi.

2. **Xavfsiz va qulay post tarqatish:**
   - Faqat vakolatli adminlar post tarqata oladi.
   - Har qanday formatdagi postlarni qo'llab-quvvatlaydi:
     - Oddiy matn (chiroyli formatlash, havolalar bilan);
     - Rasm yoki foto albom;
     - Reklama videoroligi yoki video xabar (dumaloq video);
     - Hujjat, PDF, prezentatsiya, audio;
     - Inline tugmalarga ega postlar yoki boshqa kanallardan uzatilgan postlar.
   - `copy_message` metodi orqali yuboriladi (post tepasida "Forwarded from" belgisisiz, xuddi kanalda yozilgandek toza chiqadi).

3. **Manzilni tanlash:**
   - 🚀 **Barchasiga** (Barcha kanallar va guruhlar)
   - 📢 **Faqat kanallarga**
   - 👥 **Faqat guruhlarga**

4. **Telegram limitlari va xatoliklarni himoyalash:**
   - Flood limit (TelegramRetryAfter) kelganda avtomatik kutish va qayta urinish.
   - Bloklangan yoki yopilgan guruhlar xatolik bermaydi va avtomatik ravishda nofaol qilib qo'yiladi.
   - Jarayon tugagach, to'liq hisobot (Nechtasi muvaffaqiyatli, nechtasi yetib bormadi) taqdim etiladi.

5. **Statistika va Ro'yxat:**
   - Faol kanallar va guruhlar sonini ko'rish.
   - Ulangan kanallar va guruhlarning to'liq ro'yxatini ID lari bilan ko'rish.

---

## 🚀 O'rnatish va Ishga Tushirish

### 1. Bot Token va Admin ID ni olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring va yangi bot yarating (`/newbot`). Bot tokenni nusxalang.
2. O'zingizning Telegram ID raqamingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga kiring.

### 2. Sozlamalarni `.env` fayliga kiritish
Loyihadagi `.env` faylini oching (yoki `.env.example` dan nusxa oling) va ma'lumotlarni to'ldiring:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
DB_PATH=database.sqlite3
```
*(Agar bir nechta admin bo'lsa, ID larni vergul bilan ajrating: `ADMIN_IDS=123456789,987654321`)*

### 3. Kutubxonalarni o'rnatish
Python virtual muhitini yarating va kutubxonalarni o'rnating:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Botni ishga tushirish
```bash
python3 main.py
```

---

## 📲 Botni Kanallar va Guruhlarga Qo'shish Qoidalari

1. **Telegram Kanallarga qo'shish:**
   - Kanalingizga kiring -> Sozlamalar -> **Administrators** -> **Add Administrator**.
   - Botingiz username'ini yozib admin qiling.
   - **Post Messages** (Xabarlarni joylashtirish) ruxsatini yoqing.
   - *Bot avtomatik ravishda bazaga qo'shiladi va sizga bu haqda xabar keladi.*

2. **Telegram Guruhlarga qo'shish:**
   - Guruhingizga botni a'zo sifatida qo'shing. (Agar guruhda faqat adminlar yoza oladigan qilib cheklangan bo'lsa, botni ham guruh administratori qiling).
   - *Bot avtomatik ravishda bazaga qo'shiladi.*

---

## 📢 Yangilik Tarqatish Tartibi

1. Botingizga kiring va `/start` bosing.
2. **"📢 Yangilik tarqatish"** tugmasini bosing.
3. Reklama roligi, video, rasm yoki matnli xabarni botga yuboring.
4. Bot sizga tasdiqlash tugmalarini ko'rsatadi:
   - `🚀 Barchasiga`
   - `📢 Kanallarga`
   - `👥 Guruhlarga`
5. Kerakli tugmani bosing va bot barcha manzillarga xabarni tarqatib, yakuniy hisobotni chiqarib beradi.
