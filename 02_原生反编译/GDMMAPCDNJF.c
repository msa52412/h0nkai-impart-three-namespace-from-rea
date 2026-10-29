
byte bVar1;
int iVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x181bd8ed3;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x134b);
if (bVar1 == 0) {
  this = (JGPPIJBHALG *)this->IOIJBGDABDL_k_BackingField;
  if (this == (JGPPIJBHALG *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x181bd8f0e;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18065f253;
  bVar1 = IFix::WrappersManagerImpl::IsPatched(0x134d);
  if (bVar1 == 0) {
    if ((this->NIIFGBOEDHC != 0.0) && (this->BEONKIIDBII != (undefined *)0x0)) {
      uStack_30 = 0x18065f26c;
      iVar2 = NLPHHCMPMHJ::EDHGACNINBK((NLPHHCMPMHJ *)this);
      if (iVar2 != 0) {
        return 1;
      }
    }
    return 0;
  }
  uStack_30 = 0x18065f28a;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x134d);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18065f2a4;
    il2cpp::codegen::raise_null_reference_exception();
  }
}
else {
  uStack_30 = 0x181bd8ef4;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x134b);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x181bd8f14;
    il2cpp::codegen::raise_null_reference_exception();
  }
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
if ((VirtualMachine *)pIVar3->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
           (pIVar3->anonObj != (undefined *)0x0) + 1,0);
bVar1 = IFix::Core::Call::GetBoolean(&CStack_58,0);
return bVar1;\