🐛 Muammo Tahlili
Nima bo'lyapti:

✅ Kod yuborilmoqda (Telegram SMS/notif yubordi)
✅ Foydalanuvchi kodni kiritdi (41697)
❌ "Tekshirilmoqda..." — bu yerda qolib ketmoqda
❌ "Kod muddati tugagan" — aslida kod yangi bo'lsa ham

🔍 Asosiy Sabablar
1. Handler await ni kutmayapti (eng ko'p uchraydigan bug)
python# ❌ NOTO'G'RI
@dp.message_handler()
def get_code(message):
    client.sign_in(phone, code=message.text)  # async funksiya sync da

# ✅ TO'G'RI
@dp.message(F.text)
async def get_code(message: Message, state: FSMContext):
    data = await state.get_data()
    await client.sign_in(data['phone'], code=message.text.strip())
2. FSM State yo'qolishi
python# ❌ State saqlanmagan
async def send_code(message):
    await client.send_code(phone)
    # state ga phone saqlanmagan!

# ✅ State ga saqla
async def send_code(message, state: FSMContext):
    sent = await client.send_code(phone)
    await state.update_data(
        phone=phone,
        phone_code_hash=sent.phone_code_hash  # BU MUHIM!
    )
    await state.set_state(AuthStates.waiting_code)
3. phone_code_hash yo'q (ENG KO'P UCHRAYDIGAN)
python# ✅ sign_in da hash kerak
async def verify_code(message, state: FSMContext):
    data = await state.get_data()
    
    await client.sign_in(
        phone=data['phone'],
        code=message.text.strip(),
        phone_code_hash=data['phone_code_hash']  # ← BU BO'LMASA KOD EXPIRE BO'LADI
    )
4. 30 soniya — juda qisqa timeout
python# Kodni kiritish uchun vaqtni ko'paytir
await asyncio.wait_for(
    verify_code_task(),
    timeout=120  # 30 emas, 120 soniya
)
✅ To'liq Ishlaydiган Kod
pythonfrom aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pyrogram import Client

class AuthStates(StatesGroup):
    waiting_phone = State()
    waiting_code = State()
    waiting_password = State()  # 2FA uchun

@router.message(Command("connect"))
async def cmd_connect(message: Message, state: FSMContext):
    await message.answer("📱 Telefon raqamingizni yuboring:\n+998901234567")
    await state.set_state(AuthStates.waiting_phone)

@router.message(AuthStates.waiting_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    
    client = Client(f"session_{message.from_user.id}", 
                    api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    
    try:
        sent = await client.send_code(phone)
        
        # ⬇️ IKKALASINI HAM SAQLASH SHART
        await state.update_data(
            phone=phone,
            phone_code_hash=sent.phone_code_hash,
            client_session=True
        )
        await state.set_state(AuthStates.waiting_code)
        
        await message.answer(
            "⏳ Kod yuborilmoqda...\n"
            "📨 Telegram sizga tasdiqlash kodi yubordi.\n\n"
            "Iltimos, kodni shu yerga yozing:\n"
            "⚠️ Muhim: Kodni tez kiriting (120 soniya ichida)!"
        )
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
        await state.clear()

@router.message(AuthStates.waiting_code)
async def get_code(message: Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    
    await message.answer("⏳ Tekshirilmoqda...")
    
    client = Client(f"session_{message.from_user.id}",
                    api_id=API_ID, api_hash=API_HASH)
    await client.connect()
    
    try:
        await client.sign_in(
            phone_number=data['phone'],
            phone_code_hash=data['phone_code_hash'],  # ← KALIT
            phone_code=code
        )
        
        await client.disconnect()
        await state.clear()
        await message.answer("✅ Muvaffaqiyatli ulandi!")
        
    except errors.SessionPasswordNeeded:
        # 2FA yoqilgan
        await state.set_state(AuthStates.waiting_password)
        await message.answer("🔐 2FA parolingizni kiriting:")
        
    except errors.PhoneCodeExpired:
        await state.clear()
        await message.answer("❌ Kod muddati tugagan.\n/connect ni qaytadan bosing.")
        
    except errors.PhoneCodeInvalid:
        await message.answer("❌ Kod noto'g'ri. Qaytadan kiriting:")
📋 Tekshirish Ro'yxati

 phone_code_hash state ga saqlanayaptimi?
 sign_in da phone_code_hash berilayaptimi?
 Handler async def bilan yozilganmi?
 Timeout 30s dan ko'proqmi?
 client.connect() chaqirilayaptimi?

Kodingizning send_code va sign_in qismini ko'rsatsangiz, aniq qaysi satrda xato borligini aytib beraman! 🎯