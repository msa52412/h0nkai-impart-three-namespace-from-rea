
longlong *plVar1;
bool bVar2;
byte bVar3;
ILFixDynamicMethodWrapper *pIVar4;
Call *pCVar5;
longlong *plVar6;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x182cc0893;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a9f);
if (bVar3 == 0) {
  plVar1 = *(longlong **)&this->levelID;
  plVar6 = (longlong *)0x0;
  if (plVar1 != (longlong *)0x0) {
    if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a15818 + 0x132)) ||
       (bVar2 = true,
       *(longlong *)
        (*(longlong *)(*plVar1 + 0x50) +
        (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8) != _DAT_189a15818)) {
      bVar2 = false;
    }
    if (bVar2) {
      plVar6 = plVar1;
    }
  }
  return plVar6 != (longlong *)0x0;
}
uStack_30 = 0x182cc08f0;
pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x19a9f);
if (pIVar4 != (ILFixDynamicMethodWrapper *)0x0) {
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
    bVar3 = IFix::Core::Call::GetBoolean(&CStack_58,0);
    return bVar3;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
uStack_30 = 0x182cc090a;
il2cpp::codegen::raise_null_reference_exception();\