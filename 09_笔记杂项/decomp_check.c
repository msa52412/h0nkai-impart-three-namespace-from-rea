// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 429990

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
    uVar2 = func_0x00018619ddd0();
    uVar3 = func_0x00018619df20(param_2);
    uVar3 = func_0x000185e90050(uVar3);
    uVar4 = thunk_FUN_1804457f0(_DAT_1899de3c0);
    ArgumentOutOfRangeException::_ctor(uVar4,uVar2,uVar3);
    FUN_1804fe3d0(uVar4,_DAT_189a69560);
    pcVar1 = (code *)swi(3);
    (*pcVar1)();
    return;
  }
  uVar3 = func_0x00018619ddd0();
  uVar2 = **(undefined8 **)(_DAT_1899de428 + 0x28);
  uVar4 = thunk_FUN_1804457f0(_DAT_1899de3c0);
  ArgumentOutOfRangeException::_ctor(uVar4,uVar3,uVar2);
  FUN_1804fe3d0(uVar4,_DAT_189a69560);
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x185E90050 ================= */
/* name   = GetText */
/* entry  = 185df3c40 */
/* body   = 199 bytes */
/* sig    = undefined GetText() */


/* WARNING: Possible PIC construction at 0x000185df3c74: Changing call to branch */
/* WARNING: Possible PIC construction at 0x000185df3ca2: Changing call to branch */
/* WARNING: Possible PIC construction at 0x000185df3ccd: Changing call to branch */
/* WARNING: Removing unreachable block (ram,0x000185df3ca7) */
/* WARNING: Removing unreachable block (ram,0x000185df3c79) */
/* WARNING: Removing unreachable block (ram,0x000185df3c9f) */
/* WARNING: Removing unreachable block (ram,0x000185df3c7d) */
/* WARNING: Removing unreachable block (ram,0x000185df3cd2) */
/* WARNING: Removing unreachable block (ram,0x000185df3cf7) */
/* WARNING: Removing unreachable block (ram,0x000185df3cd6) */
/* WARNING: Removing unreachable block (ram,0x000185bb9290) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* C#: string Locale::GetText(string msg)  [static]  token=06000005
   GENERIC-SHARED aliases (73): System::Array::get_SyncRoot;
   System::RuntimeType::get_UnderlyingSystemType; System::RuntimeType::Clone;
   System::String::ToString; System::String::ToString; System::String::Clone;
   System::TimeSpan::FromTicks; System::Environment::GetResourceString; System::IntPtr::op_Explicit;
   System::IntPtr::op_Explicit; System::IntPtr::op_Explicit; System::UIntPtr::op_Explicit;  ... */

undefined8 Locale::GetText(undefined8 param_1)

{
  int iVar1;
  
  iVar1 = func_0x000185df43f0();
  if (iVar1 == 4) {
    if (*(int *)(_DAT_1899de4b8 + 0xe8) == 0) {
      thunk_FUN_18042d860();
    }
  }
  else if (*(int *)(_DAT_1899de4b8 + 0xe8) == 0) {
    thunk_FUN_18042d860();
  }
  return param_1;
}



/* ================= 0x1858E8220 ================= */
/* name   = GetNativeStackTrace */
/* entry  = 1858e8220 */
/* body   = 5 bytes */
/* sig    = undefined GetNativeStackTrace() */


/* C#: string Runtime::GetNativeStackTrace(System.Exception exception)  [static]  token=0600000E
   GENERIC-SHARED aliases (9): System::MissingMemberException::FormatSignature;
   System::RuntimeType::get_DeclaringMethod; System::Delegate::GetVirtualMethod_internal;
   System.Reflection::MonoField::ResolveType;
   System.Reflection::MonoPropertyInfo::get_default_value; System.IO::MonoIO::DumpHandles;
   System.Threading::ThreadPool::ReportThreadStatus;
   System.Runtime.Remoting.Contexts::Context::RegisterContext;
   System.Runtime.Remoting.Contexts::Context::ReleaseContext;  */

void Mono::Runtime::GetNativeStackTrace(void)

{
  code *pcVar1;
  
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



