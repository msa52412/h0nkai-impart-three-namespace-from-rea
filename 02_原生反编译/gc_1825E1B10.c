
longlong lVar1;
byte bVar2;
ILFixDynamicMethodWrapper *pIVar3;
Call *pCVar4;
Call CStack_58;

CStack_58.currentTop = (undefined *)0x1825e1b2a;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9c15);
if (bVar2 == 0) {
  *(Action **)&this->displayStep = nextTaskCallback;
  CStack_58.currentTop = (undefined *)0x1825e1b43;
  MonoBaseUIComponent::SafeSetActive((MonoBaseUIComponent *)this,1);
  CStack_58.currentTop = (undefined *)0x1825e1b4d;
  SetOnceEffectActive(this,1);
  CStack_58.currentTop = (undefined *)0x1825e1b57;
  SetContinueEffectActive(this,1);
  CStack_58.currentTop = (undefined *)0x1825e1b5f;
  PlayAnimationStep1(this);
  lVar1 = *_DAT_189a98a58;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    CStack_58.currentTop = (undefined *)0x1825e1b7a;
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    CStack_58.currentTop = (undefined *)0x1825e1b95;
    FUN_18043e4c0(lVar1);
  }
  if ((WwiseAudioManager *)**(undefined8 **)(lVar1 + 0x28) != (WwiseAudioManager *)0x0) {
    CStack_58.currentTop = (undefined *)0x1825e1bc8;
    WwiseAudioManager::Post
              ((WwiseAudioManager *)**(undefined8 **)(lVar1 + 0x28),_DAT_189b739a0,
               (GameObject *)0x0,(EventCallback *)0x0,(EventCallback *)0x0,_DAT_189b4a238);
    return;
  }
                  /* WARNING: Subroutine does not return */
  CStack_58.currentTop = (undefined *)0x1825e1bff;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.currentTop = (undefined *)0x1825e1bdd;
pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9c15);
if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.currentTop = (undefined *)0x1825e1c05;
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
IFix::Core::Call::PushObject(&CStack_58,(undefined *)nextTaskCallback);
if ((VirtualMachine *)pIVar3->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar3->virtualMachine,pIVar3->methodId,&CStack_58,
             (pIVar3->anonObj != (undefined *)0x0) + 2,0);
  return;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\