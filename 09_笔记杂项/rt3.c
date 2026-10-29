// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x1835D7F80 ================= */
/* name   = IsPatched */
/* entry  = 1835d7f80 */
/* body   = 146 bytes */
/* sig    = byte IsPatched(int id) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: bool WrappersManagerImpl::IsPatched(int id)  [static]  token=0603900B */

byte IFix::WrappersManagerImpl::IsPatched(int id)

{
  longlong lVar1;
  code *pcVar2;
  byte bVar3;
  undefined8 uVar4;
  
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    il2cpp::vm::Class::Init();
  }
  if (**(longlong **)(_DAT_189a34088 + 0x28) == 0) {
    il2cpp::codegen::codegen::raise_null_reference_exception();
    pcVar2 = (code *)swi(3);
    bVar3 = (*pcVar2)();
    return bVar3;
  }
  if (*(int *)(**(longlong **)(_DAT_189a34088 + 0x28) + 0x18) <= id) {
    return 0;
  }
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    il2cpp::vm::Class::Init();
  }
  lVar1 = **(longlong **)(_DAT_189a34088 + 0x28);
  if (lVar1 != 0) {
    if ((uint)id < *(uint *)(lVar1 + 0x18)) {
      return *(longlong *)(lVar1 + 0x20 + (longlong)id * 8) != 0;
    }
    uVar4 = il2cpp::vm::Exception::CreateIndexOutOfRangeException();
    il2cpp::codegen::codegen::raise_exception(uVar4,0);
    pcVar2 = (code *)swi(3);
    bVar3 = (*pcVar2)();
    return bVar3;
  }
  il2cpp::codegen::codegen::raise_null_reference_exception();
  pcVar2 = (code *)swi(3);
  bVar3 = (*pcVar2)();
  return bVar3;
}



/* ================= 0x1835D7ED0 ================= */
/* name   = GetPatch */
/* entry  = 1835d7ed0 */
/* body   = 90 bytes */
/* sig    = ILFixDynamicMethodWrapper * GetPatch(int id) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: IFix_ILFixDynamicMethodWrapper WrappersManagerImpl::GetPatch(int id)  [static]
   token=0603900A */

ILFixDynamicMethodWrapper * IFix::WrappersManagerImpl::GetPatch(int id)

{
  longlong lVar1;
  code *pcVar2;
  undefined8 uVar3;
  ILFixDynamicMethodWrapper *pIVar4;
  
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    il2cpp::vm::Class::Init(_DAT_189a34088);
  }
  lVar1 = **(longlong **)(_DAT_189a34088 + 0x28);
  if (lVar1 != 0) {
    if ((uint)id < *(uint *)(lVar1 + 0x18)) {
      return *(ILFixDynamicMethodWrapper **)(lVar1 + 0x20 + (longlong)id * 8);
    }
    uVar3 = il2cpp::vm::Exception::CreateIndexOutOfRangeException();
    il2cpp::codegen::codegen::raise_exception(uVar3,0);
    pcVar2 = (code *)swi(3);
    pIVar4 = (ILFixDynamicMethodWrapper *)(*pcVar2)();
    return pIVar4;
  }
  il2cpp::codegen::codegen::raise_null_reference_exception();
  pcVar2 = (code *)swi(3);
  pIVar4 = (ILFixDynamicMethodWrapper *)(*pcVar2)();
  return pIVar4;
}



