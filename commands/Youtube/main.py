from aiogram import Dispatcher, types
from user import BFGuser, BFGconst
import random
from assets.antispam import antispam
import commands.Youtube.db as db
from assets.transform import transform_int as tr


@antispam
async def youtube(message: types.Message, user: BFGuser):
  if int(user.property.phone) == 0:
      await message.answer('у вас нет телефона чтобы снимать видеоролики')
      return

  if int(user.youtubekanal) == 0:
      await message.answer('У вас нет ютуб канала чтобы начать снимать видеоролики')
      return
    
  summ = random.randint(1, 2)

  
  await db.getbcoins(user.user_id, summ)
  await message.answer( f'Вы успешно сняли видеоролик, вы получили {summ}, b-coins')



  
  

def reg(dp: Dispatcher):
  dp.register_message_handler(youtube, lambda message: message.text == 'ютуб')
