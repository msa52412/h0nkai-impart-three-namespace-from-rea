
longlong *plVar1;
StorageDataItemBase *data;
DropNewNormalItemCmpt *this_00;
DropNewSpecialItemCmpt *this_01;
byte bVar2;
longlong *plVar3;
KeyGeneratedEventHandler *pKVar4;
ILFixDynamicMethodWrapper *pIVar5;
Call *pCVar6;
bool bVar7;
longlong *plVar8;
bool bVar9;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x18279ff63;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x16225);
if (bVar2 != 0) {
  uStack_30 = 0x1827a00ee;
  pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x16225);
  if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a0114;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar6 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar6->argumentBase;
  CStack_58.evaluationStackBase = pCVar6->evaluationStackBase;
  CStack_58.managedStack = pCVar6->managedStack;
  CStack_58.currentTop = pCVar6->currentTop;
  CStack_58.topWriteBack = pCVar6->topWriteBack;
  if (pIVar5->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar5->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar5->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar5->virtualMachine,pIVar5->methodId,&CStack_58,
             (pIVar5->anonObj != (undefined *)0x0) + 1,0);
  return;
}
plVar1 = (longlong *)this->data;
plVar8 = (longlong *)0x0;
if (plVar1 != (longlong *)0x0) {
  bVar9 = true;
  if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a17428 + 0x132)) ||
     (bVar7 = bVar9,
     *(longlong *)
      (*(longlong *)(*plVar1 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a17428 + 0x132) - 1) * 8)
     != _DAT_189a17428)) {
    bVar7 = false;
  }
  plVar3 = plVar8;
  if (bVar7 != false) {
    plVar3 = plVar1;
  }
  if (plVar3 != (longlong *)0x0) goto LAB_1827a000b;
}
if (plVar1 != (longlong *)0x0) {
  if ((*(byte *)(*plVar1 + 0x132) < *(byte *)(_DAT_189a18310 + 0x132)) ||
     (plVar3 = (longlong *)0x1,
     *(longlong *)
      (*(longlong *)(*plVar1 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8)
     != _DAT_189a18310)) {
    plVar3 = plVar8;
  }
  if ((char)plVar3 != '\0') {
    plVar8 = plVar1;
  }
}
bVar9 = plVar8 != (longlong *)0x0;
LAB_1827a000b:
uStack_30 = 0x1827a002b;
UnityEngine::ComponentExtensions::SafeSetActive
          (this->normalItemCmpt,bVar9 ^ 1,CONCAT71((int7)((ulonglong)plVar1 >> 8),1));
uStack_30 = 0x1827a003e;
UnityEngine::ComponentExtensions::SafeSetActive(this->specialItemCmpt,bVar9,1);
data = (StorageDataItemBase *)this->data;
if (bVar9 == false) {
  this_00 = (DropNewNormalItemCmpt *)this->normalItemCmpt;
  uStack_30 = 0x1827a005d;
  pKVar4 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
  uStack_30 = 0x1827a0072;
  KeyGeneratedEventHandler::_ctor(pKVar4,(undefined *)this,_DAT_189aa24d0);
  if (this_00 == (DropNewNormalItemCmpt *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a0108;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x1827a0091;
  DropNewNormalItemCmpt::SetupView(this_00,data,(Action *)pKVar4,this->onlyShow);
}
else {
  this_01 = (DropNewSpecialItemCmpt *)this->specialItemCmpt;
  uStack_30 = 0x1827a00b2;
  pKVar4 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
  uStack_30 = 0x1827a00c7;
  KeyGeneratedEventHandler::_ctor(pKVar4,(undefined *)this,_DAT_189aa24d0);
  if (this_01 == (DropNewSpecialItemCmpt *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a010e;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x1827a00e2;
  DropNewSpecialItemCmpt::SetupView(this_01,data,(Action *)pKVar4,this->onlyShow);
}
return;\