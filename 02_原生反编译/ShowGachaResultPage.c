
longlong lVar1;
byte bVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
GachaResultPageContext_New *this;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x185294e4e;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x18427);
if (bVar2 != 0) {
  uStack_30 = 0x185294ea3;
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x18427);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x185294eb9;
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
  if ((VirtualMachine *)pIVar3->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
               (uint)(pIVar3->anonObj != (undefined *)0x0),0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x185294e63;
this = (GachaResultPageContext_New *)il2cpp::codegen::object_new(_DAT_189a2b460);
uStack_30 = 0x185294e6e;
GachaResultPageContext_New::_ctor(this);
if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
  uStack_30 = 0x185294e83;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x18303e299;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0xdf4);
if (bVar2 == 0) {
  lVar1 = *_DAT_189a985c0;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18303e2bd;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    uStack_30 = 0x18303e2d8;
    FUN_18043e4c0(lVar1);
  }
  if ((MainUIManager *)**(undefined8 **)(lVar1 + 0x28) != (MainUIManager *)0x0) {
    uStack_30 = 0x18303e2f4;
    MainUIManager::ShowPage
              ((MainUIManager *)**(undefined8 **)(lVar1 + 0x28),(BasePageContext *)this,1);
  }
  return;
}
uStack_30 = 0x18303e309;
pIVar3 = IFix::WrappersManagerImpl::GetPatch(0xdf4);
if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x18303e32b;
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
IFix::Core::Call::PushInt32(&CStack_58,1);
if ((VirtualMachine *)pIVar3->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
             (pIVar3->anonObj != (undefined *)0x0) + 2,0);
  return;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\