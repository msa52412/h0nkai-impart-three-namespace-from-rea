
longlong lVar1;
StorageModule *this_00;
byte bVar2;
undefined *puVar3;
ILFixDynamicMethodWrapper *pIVar4;
Call *pCVar5;
uint uVar6;
longlong lVar7;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1816e84e3;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9bed);
if (bVar2 == 0) {
  lVar7 = *_DAT_189a9b3d8;
  if (*(char *)(lVar7 + 0x136) == '\0') {
    uStack_30 = 0x1816e8506;
    FUN_18043e4c0(lVar7);
  }
  lVar7 = **(longlong **)(lVar7 + 0x90);
  if (*(char *)(lVar7 + 0x136) == '\0') {
    uStack_30 = 0x1816e8521;
    FUN_18043e4c0(lVar7);
  }
  if ((HCHDIBFGCAL *)**(undefined8 **)(lVar7 + 0x28) != (HCHDIBFGCAL *)0x0) {
    uStack_30 = 0x1816e8540;
    puVar3 = HCHDIBFGCAL::MCLIMNCKODA((HCHDIBFGCAL *)**(undefined8 **)(lVar7 + 0x28));
    uVar6 = 0;
    if (puVar3 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1816e861c;
      il2cpp::codegen::raise_null_reference_exception();
    }
    lVar7 = 0x20;
    while( true ) {
      if (*(int *)(puVar3 + 0x18) <= (int)uVar6) {
        return;
      }
      lVar1 = *_DAT_189a98b00;
      if (*(char *)(lVar1 + 0x136) == '\0') {
        uStack_30 = 0x1816e8584;
        FUN_18043e4c0(lVar1);
      }
      lVar1 = **(longlong **)(lVar1 + 0x90);
      if (*(char *)(lVar1 + 0x136) == '\0') {
        uStack_30 = 0x1816e859f;
        FUN_18043e4c0(lVar1);
      }
      this_00 = (StorageModule *)**(undefined8 **)(lVar1 + 0x28);
      if (*(uint *)(puVar3 + 0x18) <= uVar6) {
        uStack_30 = 0x1816e85b0;
        System::ThrowHelper::ThrowArgumentOutOfRangeException();
      }
      if (*(longlong *)(lVar7 + *(longlong *)(puVar3 + 0x10)) == 0) break;
      if (this_00 == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1816e8610;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1816e85cd;
      StorageModule::RecordNewItem
                (this_00,*(int *)(*(longlong *)(lVar7 + *(longlong *)(puVar3 + 0x10)) + 0x14));
      uVar6 = uVar6 + 1;
      lVar7 = lVar7 + 8;
    }
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e8616;
    il2cpp::codegen::raise_null_reference_exception();
  }
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1816e8622;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1816e85e1;
pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x9bed);
if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1816e8628;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.argumentBase = (undefined *)0x0;
CStack_58.evaluationStackBase = (undefined *)0x0;
CStack_58.managedStack = (undefined *)0x0;
CStack_58.currentTop = (undefined *)0x0;
CStack_58.topWriteBack = (undefined *)0x0;
pCVar5 = IFix::Core::Call::Begin();
CStack_58.argumentBase = pCVar5->argumentBase;
CStack_58.evaluationStackBase = pCVar5->evaluationStackBase;
CStack_58.managedStack = pCVar5->managedStack;
CStack_58.currentTop = pCVar5->currentTop;
CStack_58.topWriteBack = pCVar5->topWriteBack;
if (pIVar4->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar4->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
if ((VirtualMachine *)pIVar4->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,&CStack_58,
             (pIVar4->anonObj != (undefined *)0x0) + 1,0);
  return;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\