
byte bVar1;
undefined *puVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
Call CStack_68;
undefined8 uStack_40;

uStack_40 = 0x182cc0c23;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x12e19);
if (bVar1 == 0) {
  uStack_40 = 0x182cc0c36;
  puVar2 = Coroutine_AvatarEffect(this,delay,isRareDrop);
                  /* WARNING: Could not recover jumptable at 0x0001869131b0. Too many branches */
                  /* WARNING: Treating indirect jump as call */
  (*_DAT_1899d7cd0)(this,puVar2);
  return;
}
uStack_40 = 0x182cc0c5a;
pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x12e19);
if (pIVar3 != (ILFixDynamicMethodWrapper *)0x0) {
  CStack_68.argumentBase = (undefined *)0x0;
  CStack_68.evaluationStackBase = (undefined *)0x0;
  CStack_68.managedStack = (undefined *)0x0;
  CStack_68.currentTop = (undefined *)0x0;
  CStack_68.topWriteBack = (undefined *)0x0;
  pCVar4 = IFix::Core::Call::Begin();
  CStack_68.argumentBase = pCVar4->argumentBase;
  CStack_68.evaluationStackBase = pCVar4->evaluationStackBase;
  CStack_68.managedStack = pCVar4->managedStack;
  CStack_68.currentTop = pCVar4->currentTop;
  CStack_68.topWriteBack = pCVar4->topWriteBack;
  if (pIVar3->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_68,pIVar3->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_68,(undefined *)this);
  IFix::Core::Call::PushSingle(&CStack_68,delay);
  IFix::Core::Call::PushBoolean(&CStack_68,isRareDrop);
  if ((VirtualMachine *)pIVar3->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_68,
               (pIVar3->anonObj != (undefined *)0x0) + 3,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
uStack_40 = 0x182cc0c85;
il2cpp::codegen::raise_null_reference_exception();\