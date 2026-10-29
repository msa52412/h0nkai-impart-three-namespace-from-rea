// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x186637860 ================= */
/* name   = _ctor */
/* entry  = 186637860 */
/* body   = 288 bytes */
/* sig    = undefined _ctor() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: void BulletinActivityConfig::_ctor()  token=0600008B */

void proto::BulletinActivityConfig::_ctor(longlong param_1)

{
  undefined8 uVar1;
  
  *(undefined8 *)(param_1 + 0x10) = 0;
  *(undefined8 *)(param_1 + 0x18) = 0;
  *(undefined4 *)(param_1 + 0x20) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0x28) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0x30) = uVar1;
  *(undefined8 *)(param_1 + 0x38) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x40) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0x48) = uVar1;
  *(undefined8 *)(param_1 + 0x50) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x58) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x60) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x68) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x70) = _DAT_189b4a238;
  *(undefined4 *)(param_1 + 0x78) = 0;
  *(undefined8 *)(param_1 + 0x80) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x88) = _DAT_189b4a238;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0x90) = uVar1;
  *(undefined8 *)(param_1 + 0x98) = _DAT_189b4a238;
  return;
}



/* ================= 0x186877340 ================= */
/* name   = global_ProtoBuf_IExtensible_GetExtensionObject */
/* entry  = 186877340 */
/* body   = 1 bytes */
/* sig    = undefined global_ProtoBuf_IExtensible_GetExtensionObject() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: ProtoBuf_IExtension
   BulletinActivityConfig::global_ProtoBuf_IExtensible_GetExtensionObject(bool createIfMissing)
   token=0600008C
   GENERIC-SHARED aliases (4):
   proto::ArmadaBriefData::global_ProtoBuf_IExtensible_GetExtensionObject;
   proto::StageBeginReq::global_ProtoBuf_IExtensible_GetExtensionObject;
   proto::Goods::global_ProtoBuf_IExtensible_GetExtensionObject;
   proto::Shop::global_ProtoBuf_IExtensible_GetExtensionObject;  */

longlong proto::BulletinActivityConfig::global_ProtoBuf_IExtensible_GetExtensionObject
                   (longlong param_1,char param_2)

{
  longlong lVar1;
  longlong *plVar2;
  
  plVar2 = (longlong *)(param_1 + 0xa0);
  if ((param_2 != '\0') && (*plVar2 == 0)) {
    lVar1 = thunk_FUN_1804457f0(_DAT_1899e55a0);
    Mono::Xml::SecurityParser::OnStartParsing(lVar1);
    *plVar2 = lVar1;
    return lVar1;
  }
  return *plVar2;
}



/* ================= 0x186AF8990 ================= */
/* name   = _ctor */
/* entry  = 186af8990 */
/* body   = 525 bytes */
/* sig    = undefined _ctor() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: void OpenworldChapter::_ctor()  token=06000139 */

void proto::OpenworldChapter::_ctor(longlong param_1)

{
  undefined8 uVar1;
  
  *(undefined4 *)(param_1 + 0x10) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e9688);
  FUN_184fb8fa0(uVar1,_DAT_189a74530);
  *(undefined8 *)(param_1 + 0x18) = uVar1;
  *(undefined4 *)(param_1 + 0x20) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e9690);
  FUN_184fb8fa0(uVar1,_DAT_189a74538);
  *(undefined8 *)(param_1 + 0x28) = uVar1;
  *(undefined8 *)(param_1 + 0x30) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0;
  *(undefined8 *)(param_1 + 0x40) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e9698);
  FUN_184fb8fa0(uVar1,_DAT_189a74540);
  *(undefined8 *)(param_1 + 0x48) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96a0);
  FUN_184fb8fa0(uVar1,_DAT_189a74548);
  *(undefined8 *)(param_1 + 0x50) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96a8);
  FUN_184fb8fa0(uVar1,_DAT_189a74550);
  *(undefined8 *)(param_1 + 0x58) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96b0);
  FUN_184fb8fa0(uVar1,_DAT_189a74558);
  *(undefined8 *)(param_1 + 0x60) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96b8);
  FUN_184fb8fa0(uVar1,_DAT_189a74560);
  *(undefined8 *)(param_1 + 0x68) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96c0);
  FUN_184fb8fa0(uVar1,_DAT_189a74568);
  *(undefined8 *)(param_1 + 0x70) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96c8);
  FUN_184fb8fa0(uVar1,_DAT_189a74570);
  *(undefined8 *)(param_1 + 0x78) = uVar1;
  *(undefined8 *)(param_1 + 0x80) = 0;
  *(undefined8 *)(param_1 + 0x88) = 0;
  *(undefined8 *)(param_1 + 0x90) = 0;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96d0);
  FUN_184fb8fa0(uVar1,_DAT_189a74578);
  *(undefined8 *)(param_1 + 0x98) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0xa0) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e96d8);
  FUN_184fb8fa0(uVar1,_DAT_189a74580);
  *(undefined8 *)(param_1 + 0xa8) = uVar1;
  uVar1 = thunk_FUN_1804457f0(_DAT_1899e69f0);
  FUN_1849b2bc0(uVar1,0);
  *(undefined8 *)(param_1 + 0xb0) = uVar1;
  return;
}



/* ================= 0x186B07D20 ================= */
/* name   = _ctor */
/* entry  = 186b07d20 */
/* body   = 219 bytes */
/* sig    = undefined _ctor() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: void PlayerLoginReq::_ctor()  token=0600000B */

void proto::PlayerLoginReq::_ctor(longlong param_1)

{
  *(undefined4 *)(param_1 + 0x10) = 0;
  *(undefined8 *)(param_1 + 0x18) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x20) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x28) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x30) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x38) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x40) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x48) = 0;
  *(undefined8 *)(param_1 + 0x50) = 0;
  *(undefined8 *)(param_1 + 0x58) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x60) = 0;
  *(undefined8 *)(param_1 + 0x68) = _DAT_189b4a238;
  *(undefined4 *)(param_1 + 0x70) = 0;
  *(undefined8 *)(param_1 + 0x78) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x80) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x88) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x90) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x98) = 0;
  *(undefined1 *)(param_1 + 0xa0) = 0;
  *(undefined4 *)(param_1 + 0xa4) = 0;
  *(undefined8 *)(param_1 + 0xa8) = _DAT_189b4a238;
  *(undefined4 *)(param_1 + 0xb0) = 0;
  *(undefined8 *)(param_1 + 0xb8) = _DAT_189b4a238;
  return;
}



/* ================= 0x186B0A680 ================= */
/* name   = _ctor */
/* entry  = 186b0a680 */
/* body   = 231 bytes */
/* sig    = undefined _ctor() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: void GetPlayerTokenReq::_ctor()  token=06000007 */

void proto::GetPlayerTokenReq::_ctor(longlong param_1)

{
  *(undefined8 *)(param_1 + 0x18) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x20) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x28) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x30) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x38) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x40) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x48) = 0;
  *(undefined8 *)(param_1 + 0x50) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x58) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x60) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x68) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x70) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x78) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x80) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0x88) = _DAT_189b4a238;
  *(undefined4 *)(param_1 + 0x90) = 0;
  *(undefined1 *)(param_1 + 0x94) = 0;
  *(undefined4 *)(param_1 + 0x98) = 0;
  *(undefined8 *)(param_1 + 0xa0) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0xa8) = _DAT_189b4a238;
  *(undefined8 *)(param_1 + 0xb0) = _DAT_189b4a238;
  return;
}



