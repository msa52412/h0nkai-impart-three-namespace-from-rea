
longlong *plVar1;
byte bVar2;
undefined *DOBLEKELDNN;
KGFADHGGGBB *this_00;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1825e2233;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9bbf);
if (bVar2 != 0) {
  uStack_30 = 0x1825e22ff;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9bbf);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e2325;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar4 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar4->argumentBase;
  CStack_58.evaluationStackBase = pCVar4->evaluationStackBase;
  CStack_58.managedStack = pCVar4->managedStack;
  CStack_58.currentTop = pCVar4->currentTop;
  CStack_58.topWriteBack = pCVar4->topWriteBack;
  if (pIVar3->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar3->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar3->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
               (pIVar3->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
plVar1 = *(longlong **)&this->mainItemType;
if (plVar1 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1825e231f;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1825e2260;
DOBLEKELDNN = (undefined *)(**(code **)(*plVar1 + 0x208))(plVar1,*(undefined8 *)(*plVar1 + 0x210))
;
if (*(int *)&this->viceNumText == 3) {
  if (*(int *)(_DAT_1899fcdb0 + 0xe8) == 0) {
    uStack_30 = 0x1825e2281;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x1825e2289;
  this_00 = ExcelMeta::AGFNINPEFMH::IIPGEBNJIAH(DOBLEKELDNN);
  if (this_00 != (KGFADHGGGBB *)0x0) {
    uStack_30 = 0x1825e2296;
    DOBLEKELDNN = ExcelMeta::KGFADHGGGBB::MKNGMKAAALB(this_00);
  }
}
uStack_30 = 0x1825e22a8;
UnityEngine::UI::ImageExtensions::SafeSetSprite(this->animation,DOBLEKELDNN,1);
uStack_30 = 0x1825e22be;
SetImageRect(this,(Image *)this->animation,*(StorageDataItemBase **)&this->mainItemType,1);
uStack_30 = 0x1825e22c9;
bVar2 = UnityEngine::Object::op_Inequality((Object *)this->mainIconImg,(Object *)0x0);
if (bVar2 != 0) {
  if (this->mainIconImg != (undefined *)0x0) {
                  /* WARNING: Could not recover jumptable at 0x000186a4be40. Too many branches */
                  /* WARNING: Treating indirect jump as call */
    (*_DAT_1899d81e0)(this->mainIconImg,*(int *)&this->viceNumText == 5);
    return;
  }
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1825e2319;
  il2cpp::codegen::raise_null_reference_exception();
}
return;\