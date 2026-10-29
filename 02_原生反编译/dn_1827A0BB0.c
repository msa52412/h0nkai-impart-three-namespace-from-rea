
CanvasTimer *this_00;
byte bVar1;
ILFixDynamicMethodWrapper *pIVar2;
Call *pCVar3;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1827a0bc3;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x16243);
if (bVar1 == 0) {
  this = (DropNewNormalItemCmpt *)this->data;
  if (this == (DropNewNormalItemCmpt *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a0bfe;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x181fa0c33;
  bVar1 = IFix::WrappersManagerImpl::IsPatched(0x1622e);
  if (bVar1 == 0) {
    if ((ArrayList *)this->m_CachedPtr == (ArrayList *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x181fa0c9c;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x181fa0c47;
    System::Collections::ArrayList::Clear((ArrayList *)this->m_CachedPtr);
    this_00 = *(CanvasTimer **)&this->enableDeliveryMsgToSonCmpt;
    *(undefined1 *)((longlong)&this->listenPacketDict + 5) = 0;
    if (this_00 == (CanvasTimer *)0x0) {
      return;
    }
    uStack_30 = 0x181fa0c59;
    CanvasTimer::StopRun(this_00);
    this = *(DropNewNormalItemCmpt **)&this->enableDeliveryMsgToSonCmpt;
    if (this == (DropNewNormalItemCmpt *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x181fa0c96;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x180b90b13;
    bVar1 = IFix::WrappersManagerImpl::IsPatched(0x5728);
    if (bVar1 == 0) {
      *(undefined1 *)((longlong)&this->autoDestroyNodeSet + 5) = 1;
      this->OffsetOfInstanceIDInCPlusPlusObject = 0;
      this->pad_1C[0] = 0;
      this->pad_1C[1] = 0;
      this->pad_1C[2] = 0;
      this->pad_1C[3] = 0;
      this->parentCtx = (undefined *)0x0;
      return;
    }
    uStack_30 = 0x180b90b35;
    pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x5728);
    if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x180b90b4f;
      il2cpp::codegen::raise_null_reference_exception();
    }
  }
  else {
    uStack_30 = 0x181fa0c7c;
    pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x1622e);
    if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x181fa0ca2;
      il2cpp::codegen::raise_null_reference_exception();
    }
  }
}
else {
  uStack_30 = 0x1827a0be4;
  pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x16243);
  if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a0c04;
    il2cpp::codegen::raise_null_reference_exception();
  }
}
CStack_58.argumentBase = (undefined *)0x0;
CStack_58.evaluationStackBase = (undefined *)0x0;
CStack_58.managedStack = (undefined *)0x0;
CStack_58.currentTop = (undefined *)0x0;
CStack_58.topWriteBack = (undefined *)0x0;
pCVar3 = IFix::Core::Call::Begin();
CStack_58.argumentBase = pCVar3->argumentBase;
CStack_58.evaluationStackBase = pCVar3->evaluationStackBase;
CStack_58.managedStack = pCVar3->managedStack;
CStack_58.currentTop = pCVar3->currentTop;
CStack_58.topWriteBack = pCVar3->topWriteBack;
if (pIVar2->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar2->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
if ((VirtualMachine *)pIVar2->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar2->virtualMachine,pIVar2->methodId,&CStack_58,
           (pIVar2->anonObj != (undefined *)0x0) + 1,0);
return;\