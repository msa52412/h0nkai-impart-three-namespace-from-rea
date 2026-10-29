// program: UserAssembly_fixed.dll
// imageBase: 180000000
// functions in db: 443209

/* ================= 0x1804FE400 ================= */
/* name   = FUN_1804fe400 */
/* entry  = 1804fe400 */
/* body   = 10 bytes */
/* sig    = undefined FUN_1804fe400() */


void FUN_1804fe400(void)

{
  code *pcVar1;
  
  FUN_180448970();
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x1804FE480 ================= */
/* name   = thunk_FUN_18042d860 */
/* entry  = 1804fe480 */
/* body   = 5 bytes */
/* sig    = undefined thunk_FUN_18042d860() */


void thunk_FUN_18042d860(longlong param_1)

{
  int iVar1;
  longlong lVar2;
  undefined8 uVar3;
  undefined8 *puVar4;
  undefined8 ****ppppuVar5;
  bool bVar6;
  longlong lStackX_8;
  undefined8 uStackX_10;
  undefined8 uVar7;
  undefined8 ***apppuStack_50 [3];
  ulonglong uStack_38;
  undefined1 auStack_30 [40];
  
  uVar7 = 0xfffffffffffffffe;
  if (*(int *)(param_1 + 0xe8) == 0) {
    func_0x0001803f4990(0x1899db878);
    LOCK();
    bVar6 = *(int *)(param_1 + 0xe8) == 1;
    if (bVar6) {
      *(int *)(param_1 + 0xe8) = 1;
    }
    UNLOCK();
    if (bVar6) {
      func_0x0001803f72c0(0x1899db878);
    }
    else {
      LOCK();
      bVar6 = *(int *)(param_1 + 0xe4) == 1;
      if (bVar6) {
        *(int *)(param_1 + 0xe4) = 1;
      }
      UNLOCK();
      if (bVar6) {
        func_0x0001803f72c0(0x1899db878);
        lVar2 = FUN_1803f1b60();
        LOCK();
        bVar6 = lVar2 == *(longlong *)(param_1 + 0xf0);
        if (bVar6) {
          *(longlong *)(param_1 + 0xf0) = lVar2;
        }
        UNLOCK();
        if (!bVar6) {
          LOCK();
          iVar1 = *(int *)(param_1 + 0xe8);
          if (iVar1 == 1) {
            *(int *)(param_1 + 0xe8) = 1;
            iVar1 = 1;
          }
          UNLOCK();
          while (iVar1 == 0) {
            thunk_FUN_1803f70b0(1,0);
            LOCK();
            iVar1 = *(int *)(param_1 + 0xe8);
            if (iVar1 == 1) {
              *(int *)(param_1 + 0xe8) = 1;
              iVar1 = 1;
            }
            UNLOCK();
          }
        }
      }
      else {
        uVar3 = FUN_1803f1b60();
        LOCK();
        *(undefined8 *)(param_1 + 0xf0) = uVar3;
        UNLOCK();
        LOCK();
        *(undefined4 *)(param_1 + 0xe4) = 1;
        UNLOCK();
        func_0x0001803f72c0(0x1899db878);
        lStackX_8 = 0;
        lVar2 = FUN_180432660(param_1);
        if (lVar2 != 0) {
          FUN_180440e30(lVar2,0,0,&lStackX_8,uVar7);
        }
        LOCK();
        *(undefined4 *)(param_1 + 0xe8) = 1;
        UNLOCK();
        LOCK();
        *(undefined8 *)(param_1 + 0xf0) = 0;
        UNLOCK();
        if (lStackX_8 != 0) {
          puVar4 = (undefined8 *)FUN_180438230(auStack_30,param_1 + 0x60,0);
          if (0xf < (ulonglong)puVar4[3]) {
            puVar4 = (undefined8 *)*puVar4;
          }
          FUN_1804f17f0(apppuStack_50,&UNK_1881a2ec0,puVar4);
          FUN_1803ed580(auStack_30);
          ppppuVar5 = apppuStack_50;
          if (0xf < uStack_38) {
            ppppuVar5 = (undefined8 ****)apppuStack_50[0];
          }
          uVar7 = FUN_18043b460(ppppuVar5,lStackX_8);
          FUN_180447cf0(uVar7,0);
          uStackX_10 = uVar7;
          FUN_1804ff8e0(&uStackX_10,&UNK_188d08588);
        }
      }
    }
  }
  return;
}



/* ================= 0x1804FE3C0 ================= */
/* name   = thunk_FUN_1804457f0 */
/* entry  = 1804fe3c0 */
/* body   = 5 bytes */
/* sig    = undefined thunk_FUN_1804457f0() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong * thunk_FUN_1804457f0(longlong param_1)

{
  longlong lVar1;
  longlong *plVar2;
  
  FUN_18043d300();
  if (*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) {
    lVar1 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0));
    if (lVar1 == _DAT_1899db360) {
      param_1 = FUN_180430150(**(undefined8 **)
                                (*(longlong *)(*(longlong *)(param_1 + 0xc0) + 8) + 8),1);
    }
  }
  if (*(char *)(param_1 + 0x13a) == '\0') {
    plVar2 = (longlong *)FUN_180445bf0(param_1);
  }
  else if (*(longlong *)(param_1 + 8) == 0) {
    plVar2 = (longlong *)func_0x0001804df170(*(undefined4 *)(param_1 + 0x114));
    *plVar2 = param_1;
  }
  else {
    plVar2 = (longlong *)FUN_1804dc0e0(*(undefined4 *)(param_1 + 0x114),param_1);
  }
  if (*(char *)(param_1 + 0x13b) != '\0') {
    FUN_1804fb750(plVar2);
  }
  FUN_18042d860(param_1);
  return plVar2;
}



/* ================= 0x1804FE3D0 ================= */
/* name   = FUN_1804fe3d0 */
/* entry  = 1804fe3d0 */
/* body   = 10 bytes */
/* sig    = undefined FUN_1804fe3d0() */


void FUN_1804fe3d0(void)

{
  code *pcVar1;
  
  FUN_180448320();
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



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
    thunk_FUN_18042d860();
  }
  if (**(longlong **)(_DAT_189a34088 + 0x28) == 0) {
    FUN_1804fe400();
    pcVar2 = (code *)swi(3);
    bVar3 = (*pcVar2)();
    return bVar3;
  }
  if (*(int *)(**(longlong **)(_DAT_189a34088 + 0x28) + 0x18) <= id) {
    return 0;
  }
  if (*(int *)(_DAT_189a34088 + 0xe8) == 0) {
    thunk_FUN_18042d860();
  }
  lVar1 = **(longlong **)(_DAT_189a34088 + 0x28);
  if (lVar1 != 0) {
    if ((uint)id < *(uint *)(lVar1 + 0x18)) {
      return *(longlong *)(lVar1 + 0x20 + (longlong)id * 8) != 0;
    }
    uVar4 = thunk_FUN_180436120();
    FUN_1804fe3d0(uVar4,0);
    pcVar2 = (code *)swi(3);
    bVar3 = (*pcVar2)();
    return bVar3;
  }
  FUN_1804fe400();
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
    thunk_FUN_18042d860(_DAT_189a34088);
  }
  lVar1 = **(longlong **)(_DAT_189a34088 + 0x28);
  if (lVar1 != 0) {
    if ((uint)id < *(uint *)(lVar1 + 0x18)) {
      return *(ILFixDynamicMethodWrapper **)(lVar1 + 0x20 + (longlong)id * 8);
    }
    uVar3 = thunk_FUN_180436120();
    FUN_1804fe3d0(uVar3,0);
    pcVar2 = (code *)swi(3);
    pIVar4 = (ILFixDynamicMethodWrapper *)(*pcVar2)();
    return pIVar4;
  }
  FUN_1804fe400();
  pcVar2 = (code *)swi(3);
  pIVar4 = (ILFixDynamicMethodWrapper *)(*pcVar2)();
  return pIVar4;
}



/* ================= 0x18043E4C0 ================= */
/* name   = FUN_18043e4c0 */
/* entry  = 18043e4c0 */
/* body   = 134 bytes */
/* sig    = undefined FUN_18043e4c0() */


undefined1 FUN_18043e4c0(longlong param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  code *pcVar1;
  undefined1 uVar2;
  undefined8 uVar3;
  undefined8 auStackX_8 [4];
  undefined8 uVar4;
  
  uVar4 = 0xfffffffffffffffe;
  if (*(char *)(param_1 + 0x13f) == '\0') {
    auStackX_8[0] = 0x1899db6b0;
    func_0x0001803f4990();
    FUN_18043e550(param_1,auStackX_8);
    func_0x0001803f72c0(auStackX_8[0]);
  }
  if (*(char *)(param_1 + 0x13d) != '\0') {
    uVar3 = FUN_1804fb2f0(*(undefined4 *)(param_1 + 0xe0));
    FUN_180447cf0(uVar3,0,param_3,param_4,uVar4);
    auStackX_8[0] = uVar3;
    FUN_1804ff8e0(auStackX_8,&UNK_188d08588);
    pcVar1 = (code *)swi(3);
    uVar2 = (*pcVar1)();
    return uVar2;
  }
  return 1;
}



/* ================= 0x1804FE210 ================= */
/* name   = thunk_FUN_180436120 */
/* entry  = 1804fe210 */
/* body   = 5 bytes */
/* sig    = undefined thunk_FUN_180436120() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 thunk_FUN_180436120(void)

{
  undefined8 uVar1;
  
  uVar1 = FUN_18042d650(_DAT_1899db1c0,&UNK_1881a1de8,&UNK_1881a1f18);
  uVar1 = FUN_1804457f0(uVar1);
  FUN_180446020(uVar1,0);
  return uVar1;
}



/* ================= 0x1803EE250 ================= */
/* name   = thunk_FUN_18042cf20 */
/* entry  = 1803ee250 */
/* body   = 5 bytes */
/* sig    = undefined thunk_FUN_18042cf20() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong thunk_FUN_18042cf20(longlong param_1,longlong *param_2,undefined8 param_3,
                            undefined8 param_4)

{
  int iVar1;
  longlong lVar2;
  longlong lStackX_8;
  undefined8 uVar3;
  
  uVar3 = 0xfffffffffffffffe;
  if (*(char *)(param_1 + 0x13f) == '\0') {
    lStackX_8 = 0x1899db6b0;
    func_0x0001803f4990();
    FUN_18043e550(param_1,&lStackX_8);
    func_0x0001803f72c0(lStackX_8);
  }
  if (*(char *)(param_1 + 0x142) == '\0') {
    lVar2 = *param_2;
  }
  else {
    if ((*(undefined4 **)(param_1 + 0xc0) != (undefined4 *)0x0) &&
       (lVar2 = FUN_18043b320(**(undefined4 **)(param_1 + 0xc0)), lVar2 == _DAT_1899db360)) {
      param_1 = FUN_180430150(**(undefined8 **)
                                (*(longlong *)(*(longlong *)(param_1 + 0xc0) + 8) + 8),1);
      FUN_18043d300(param_1);
      if (*(char *)(((ulonglong)*(uint *)(param_1 + 0x114) - 0x10) + (longlong)param_2) == '\0') {
        return 0;
      }
    }
    iVar1 = *(int *)(param_1 + 0x114);
    lVar2 = FUN_1804457f0(param_1);
    FUN_180500230(lVar2 + 0x10,param_2,(longlong)iVar1 + -0x10,param_4,uVar3);
  }
  return lVar2;
}



/* ================= 0x183B83B70 ================= */
/* name   = Gen_Wrap_13 */
/* entry  = 183b83b70 */
/* body   = 179 bytes */
/* sig    = void Gen_Wrap_13(ILFixDynamicMethodWrapper * this, pointer P0) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: void ILFixDynamicMethodWrapper::Gen_Wrap_13(object P0)  token=060047F7
   GENERIC-SHARED aliases (70): IFix::ILFixDynamicMethodWrapper::Gen_Wrap_0;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_65; IFix::ILFixDynamicMethodWrapper::Gen_Wrap_452;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_654; IFix::ILFixDynamicMethodWrapper::Gen_Wrap_715;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_716; IFix::ILFixDynamicMethodWrapper::Gen_Wrap_820;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_880; IFix::ILFixDynamicMethodWrapper::Gen_Wrap_1162;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_1370; IFix::ILFixDynamicMethodWrapper::Gen_Wrap_1422;
   IFix::ILFixDynamicMethodWrapper::Gen_Wrap_2077;  ... */

void IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(ILFixDynamicMethodWrapper *this,undefined *P0)

{
  code *pcVar1;
  Call *pCVar2;
  Call aCStack_58 [2];
  
  aCStack_58[0].argumentBase = (undefined *)0x0;
  aCStack_58[0].evaluationStackBase = (undefined *)0x0;
  aCStack_58[0].managedStack = (undefined *)0x0;
  aCStack_58[0].currentTop = (undefined *)0x0;
  aCStack_58[0].topWriteBack = (undefined *)0x0;
  pCVar2 = IFix::Core::Call::Begin();
  aCStack_58[0].argumentBase = pCVar2->argumentBase;
  aCStack_58[0].evaluationStackBase = pCVar2->evaluationStackBase;
  aCStack_58[0].managedStack = pCVar2->managedStack;
  aCStack_58[0].currentTop = pCVar2->currentTop;
  aCStack_58[0].topWriteBack = pCVar2->topWriteBack;
  if (this->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(aCStack_58,this->anonObj);
  }
  IFix::Core::Call::PushObject(aCStack_58,P0);
  if ((VirtualMachine *)this->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)this->virtualMachine,this->methodId,aCStack_58,
               (this->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
  FUN_1804fe400();
  pcVar1 = (code *)swi(3);
  (*pcVar1)();
  return;
}



/* ================= 0x1804FE260 ================= */
/* name   = thunk_FUN_180436090 */
/* entry  = 1804fe260 */
/* body   = 5 bytes */
/* sig    = undefined thunk_FUN_180436090() */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 thunk_FUN_180436090(int param_1)

{
  if (param_1 == -1) {
    return 0;
  }
  return *(undefined8 *)(_DAT_1881a3628 + (longlong)param_1 * 8);
}



/* ================= 0x185F64590 ================= */
/* name   = GetTypeFromHandle */
/* entry  = 185f64590 */
/* body   = 76 bytes */
/* sig    = Type * GetTypeFromHandle(RuntimeTypeHandle handle) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */
/* C#: System_Type Type::GetTypeFromHandle(System.RuntimeTypeHandle handle)  [static]
   token=06000D3C */

Type * System::Type::GetTypeFromHandle(RuntimeTypeHandle handle)

{
  byte bVar1;
  Type *pTVar2;
  
  bVar1 = RuntimeType::op_Equality((RuntimeType *)handle.value,(RuntimeType *)0x0);
  if (bVar1 == 0) {
    if (*(int *)(_DAT_1899de380 + 0xe8) == 0) {
      thunk_FUN_18042d860();
    }
    pTVar2 = (Type *)thunk_FUN_18043b300(handle.value);
    return pTVar2;
  }
  return (Type *)0x0;
}



