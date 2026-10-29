
undefined *puVar1;
MonoGachaSettlementIconCmpt *this_00;
byte bVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1816e96d1;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9c13);
if (bVar2 == 0) {
  this = (GachaSequencePageContext *)this->settlementPanel;
  if (this == (GachaSequencePageContext *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e972e;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x18260e392;
  bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9c14);
  if (bVar2 == 0) {
    puVar1 = this->bindedEvents;
    if (puVar1 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x18260e419;
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (*(uint *)(puVar1 + 0x18) <= (uint)index) {
      uStack_30 = 0x18260e3ae;
      System::ThrowHelper::ThrowArgumentOutOfRangeException();
    }
    this_00 = *(MonoGachaSettlementIconCmpt **)
               (*(longlong *)(puVar1 + 0x10) + 0x20 + (longlong)index * 8);
    if (this_00 == (MonoGachaSettlementIconCmpt *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x18260e413;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x18260e3c4;
    MonoGachaSettlementIconCmpt::Play(this_00,nextTaskCallback);
    *(int *)((longlong)&this->touchUtil + 4) = index;
    return;
  }
  uStack_30 = 0x18260e3e9;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9c14);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x18260e41f;
    il2cpp::codegen::raise_null_reference_exception();
  }
}
else {
  uStack_30 = 0x1816e9704;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9c13);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e9734;
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
IFix::Core::Call::PushInt32(&CStack_58,index);
IFix::Core::Call::PushObject(&CStack_58,(undefined *)nextTaskCallback);
if ((VirtualMachine *)pIVar3->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
           (pIVar3->anonObj != (undefined *)0x0) + 3,0);
return;\