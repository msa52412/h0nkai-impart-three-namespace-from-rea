
longlong lVar1;
BaseMonoCanvas *this_00;
LNFBAFMHDEH *this_01;
float P3;
byte bVar2;
CanvasTimer *pCVar3;
KeyGeneratedEventHandler *this_02;
ILFixDynamicMethodWrapper *pIVar4;
Call *pCVar5;
undefined *puStack_58;
undefined *puStack_50;
undefined *puStack_48;
undefined *puStack_40;

bVar2 = IFix::WrappersManagerImpl::IsPatched(0x16262);
P3 = _DAT_187975ba0;
if (bVar2 != 0) {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x16262);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  puStack_58 = (undefined *)0x0;
  puStack_50 = (undefined *)0x0;
  puStack_48 = (undefined *)0x0;
  puStack_40 = (undefined *)0x0;
  pCVar5 = IFix::Core::Call::Begin();
  puStack_58 = pCVar5->argumentBase;
  puStack_50 = pCVar5->evaluationStackBase;
  puStack_48 = pCVar5->managedStack;
  puStack_40 = pCVar5->currentTop;
  if (pIVar4->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject((Call *)&puStack_58,pIVar4->anonObj);
  }
  IFix::Core::Call::PushObject((Call *)&puStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar4->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,(Call *)&puStack_58,
               (pIVar4->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
this_01 = (LNFBAFMHDEH *)this->data;
if (this_01 == (LNFBAFMHDEH *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
bVar2 = IFix::WrappersManagerImpl::IsPatched(0xc67);
if (bVar2 == 0) {
  this_01->CEADICKDDPI = P3;
  this_01->FLKKOBNGADO = 0;
  bVar2 = UnityEngine::Mathf::Approximately(0.0,0.0);
  if (bVar2 == 0) {
    lVar1 = *_DAT_189a985c0;
    if (*(char *)(lVar1 + 0x136) == '\0') {
      FUN_18043e4c0(lVar1);
    }
    lVar1 = **(longlong **)(lVar1 + 0x90);
    if (*(char *)(lVar1 + 0x136) == '\0') {
      FUN_18043e4c0(lVar1);
    }
    if (**(longlong **)(lVar1 + 0x28) == 0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    this_00 = *(BaseMonoCanvas **)(**(longlong **)(lVar1 + 0x28) + 0x10);
    if (this_00 == (BaseMonoCanvas *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    pCVar3 = BaseMonoCanvas::CreateTimer(this_00,0.0,0.0);
    this_01->IGHJDGOBBJB = (undefined *)pCVar3;
    this_02 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
    KeyGeneratedEventHandler::_ctor(this_02,(undefined *)this_01,_DAT_189ac8708);
    if (pCVar3 == (CanvasTimer *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    pCVar3->timeUpCallback = (undefined *)this_02;
  }
  else {
    LNFBAFMHDEH::FGFLPIOBPEN(this_01);
  }
}
else {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0xc67);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_815
            ((ILFixDynamicMethodWrapper_57479 *)pIVar4,(undefined *)this_01,0.0,0,P3);
}
return;\