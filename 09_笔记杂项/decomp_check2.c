// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 442478

/* ================= 0x186AFDD50 ================= */
/* name   = GetRootAsActionArg_ApplyLevelBuff */
/* entry  = 186afdd50 */
/* body   = 119 bytes */
/* sig    = undefined GetRootAsActionArg_ApplyLevelBuff() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: MoleMole_MPProtocol_ActionArg_ApplyLevelBuff
   ActionArg_ApplyLevelBuff::GetRootAsActionArg_ApplyLevelBuff(FlatBuffers.ByteBuffer _bb)  [static]
   token=06000001 */

longlong MoleMole::MPProtocol::ActionArg_ApplyLevelBuff::GetRootAsActionArg_ApplyLevelBuff
                   (longlong param_1)

{
  code *pcVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  longlong lVar5;
  
  lVar5 = thunk_FUN_1804457f0(_DAT_1899e49e0);
  Mono::Xml::SecurityParser::probe_1826b9250(lVar5);
  if (param_1 == 0) {
    FUN_1804fe400();
    pcVar1 = (code *)swi(3);
    lVar5 = (*pcVar1)();
    return lVar5;
  }
  uVar2 = func_0x000186a650f0(param_1);
  iVar3 = func_0x000186b0b910(param_1,uVar2);
  iVar4 = func_0x000186a650f0(param_1);
  if (lVar5 != 0) {
    *(longlong *)(lVar5 + 0x18) = param_1;
    *(int *)(lVar5 + 0x10) = iVar4 + iVar3;
    return lVar5;
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  lVar5 = (*pcVar1)();
  return lVar5;
}



/* ================= 0x186AED1E0 ================= */
/* name   = init */
/* entry  = 186aebd80 */
/* body   = 83 bytes */
/* sig    = undefined init() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: MoleMole_MPProtocol_ActionArg_ApplyLevelBuff ActionArg_ApplyLevelBuff::init(int _i,
   FlatBuffers.ByteBuffer _bb)  token=06000003
   GENERIC-SHARED aliases (137): MoleMole.MPProtocol::ActionArg_SpawnPropObject::init;
   MoleMole.MPProtocol::ActionArg_CreateGoods::init;
   MoleMole.MPProtocol::ActionArg_TriggerAbility::init;
   MoleMole.MPProtocol::ActionArg_DotAttackerID::init; MoleMole.MPProtocol::MixinArg_Evade::init;
   MoleMole.MPProtocol::MixinArg_HitExplodeMixin::init;
   MoleMole.MPProtocol::MixinArg_FieldState::init; MoleMole.MPProtocol::MixinArg_BlackHole::init;
   MoleMole.MPProtocol::MixinArg_FlashBomb::init; MoleMole.MPProtocol::MixinArg_SmokeBomb::init;
   MoleMole.MPProtocol::MixinArg_SmokeBombFieldState::init;
   MoleMole.MPProtocol::MixinArg_AbilityStart::init;  ... */

longlong MoleMole::MPProtocol::ActionArg_ApplyLevelBuff::init(longlong param_1)

{
  undefined8 uVar1;
  code *pcVar2;
  longlong lVar3;
  
  lVar3 = thunk_FUN_1804457f0(_DAT_1899e4a98);
  Mono::Xml::SecurityParser::probe_1826b9250(lVar3);
  if (lVar3 != 0) {
    uVar1 = *(undefined8 *)(param_1 + 0x18);
    *(undefined4 *)(lVar3 + 0x10) = *(undefined4 *)(param_1 + 0x10);
    *(undefined8 *)(lVar3 + 0x18) = uVar1;
    return lVar3;
  }
  FUN_1804fe400();
  pcVar2 = (code *)swi(3);
  lVar3 = (*pcVar2)();
  return lVar3;
}



/* ================= 0x18619E1F0 ================= */
/* name   = ThrowArgumentOutOfRangeException */
/* entry  = 18619e1f0 */
/* body   = 173 bytes */
/* sig    = undefined ThrowArgumentOutOfRangeException() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: void ThrowHelper::ThrowArgumentOutOfRangeException(System.ExceptionArgument argument,
   System.ExceptionResource resource)  [static]  token=0600031B */

void System::ThrowHelper::ThrowArgumentOutOfRangeException(undefined8 param_1,undefined4 param_2)

{
  code *pcVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  
  if (*(char *)(*(longlong *)(_DAT_1899de648 + 0x28) + 1) == '\0') {
    uVar2 = GetArgumentName();
    uVar3 = GetResourceName(param_2);
    uVar3 = func_0x000185e90050(uVar3);
    uVar4 = thunk_FUN_1804457f0(_DAT_1899de3c0);
    ArgumentOutOfRangeException::_ctor(uVar4,uVar2,uVar3);
    FUN_1804fe3d0(uVar4,_DAT_189a69560);
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  uVar3 = GetArgumentName();
  uVar2 = **(undefined8 **)(_DAT_1899de428 + 0x28);
  uVar4 = thunk_FUN_1804457f0(_DAT_1899de3c0);
  ArgumentOutOfRangeException::_ctor(uVar4,uVar3,uVar2);
  FUN_1804fe3d0(uVar4,_DAT_189a69560);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



