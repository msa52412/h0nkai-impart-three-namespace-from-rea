
longlong *plVar1;
bool bVar2;
byte bVar3;
longlong *plVar4;
longlong lVar5;
ILFixDynamicMethodWrapper *pIVar6;
Call *pCVar7;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1825e0e13;
bVar3 = IFix::WrappersManagerImpl::IsPatched(0x9bbd);
if (bVar3 != 0) {
  uStack_30 = 0x1825e0f5c;
  pIVar6 = IFix::WrappersManagerImpl::GetPatch(0x9bbd);
  if (pIVar6 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e0f76;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar7 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar7->argumentBase;
  CStack_58.evaluationStackBase = pCVar7->evaluationStackBase;
  CStack_58.managedStack = pCVar7->managedStack;
  CStack_58.currentTop = pCVar7->currentTop;
  CStack_58.topWriteBack = pCVar7->topWriteBack;
  if (pIVar6->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar6->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar6->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar6->virtualMachine,pIVar6->methodId,&CStack_58,
               (pIVar6->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
plVar1 = *(longlong **)&this->mainItemType;
if (plVar1 != (longlong *)0x0) {
  if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a15818 + 0x132)) ||
     (bVar2 = true,
     *(longlong *)
      (*(longlong *)(*plVar1 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8)
     != _DAT_189a15818)) {
    bVar2 = false;
  }
  plVar4 = (longlong *)0x0;
  if (bVar2) {
    plVar4 = plVar1;
  }
  if (plVar4 != (longlong *)0x0) {
    *(undefined4 *)&this->viceNumText = 0;
    return;
  }
}
if (plVar1 != (longlong *)0x0) {
  if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a18310 + 0x132)) ||
     (bVar2 = true,
     *(longlong *)
      (*(longlong *)(*plVar1 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8)
     != _DAT_189a18310)) {
    bVar2 = false;
  }
  plVar4 = (longlong *)0x0;
  if (bVar2) {
    plVar4 = plVar1;
  }
  if (plVar4 != (longlong *)0x0) {
    *(undefined4 *)&this->viceNumText = 1;
    return;
  }
}
uStack_30 = 0x1825e0ee7;
lVar5 = func_0x000180257760(plVar1,_DAT_189a15a50);
if (lVar5 != 0) {
  *(undefined4 *)&this->viceNumText = 2;
  return;
}
uStack_30 = 0x1825e0efb;
lVar5 = func_0x000180257760(plVar1,_DAT_189a15a58);
if (lVar5 == 0) {
  uStack_30 = 0x1825e0f0f;
  lVar5 = func_0x000180257760(plVar1,_DAT_189a17428);
  *(uint *)&this->viceNumText = 5 - (uint)(lVar5 != 0);
  return;
}
*(undefined4 *)&this->viceNumText = 3;
return;\