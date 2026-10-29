
Object *x;
byte bVar1;
ILFixDynamicMethodWrapper *pIVar2;
GameObject *pGVar3;
Call *pCVar4;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1816e7703;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9c12);
if (bVar1 != 0) {
  uStack_30 = 0x1816e77f6;
  pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x9c12);
  if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e7822;
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
  if (pIVar2->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar2->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar2->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar2->virtualMachine,pIVar2->methodId,&CStack_58,
               (pIVar2->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1816e7719;
bVar1 = UnityEngine::Object::op_Inequality((Object *)this->stage,(Object *)0x0);
if (bVar1 != 0) {
  uStack_30 = 0x1816e7730;
  UnityEngine::ComponentExtensions::SafeSetActive(this->stage);
}
uStack_30 = 0x1816e773e;
bVar1 = UnityEngine::Object::op_Inequality((Object *)this->box,(Object *)0x0);
if (bVar1 != 0) {
  if ((MonoGachaBox *)this->box == (MonoGachaBox *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e7810;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x1816e7759;
  MonoGachaBox::SetAnimatorActive((MonoGachaBox *)this->box,1);
}
uStack_30 = 0x1816e7767;
bVar1 = UnityEngine::Object::op_Inequality((Object *)this->boxCameraAnim,(Object *)0x0);
if (bVar1 != 0) {
  if ((MonoSimpleAnimation_GachaUI *)this->boxCameraAnim == (MonoSimpleAnimation_GachaUI *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e7816;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x1816e7782;
  MonoSimpleAnimation_GachaUI::SetAnimationActive
            ((MonoSimpleAnimation_GachaUI *)this->boxCameraAnim,1);
}
uStack_30 = 0x1816e7795;
UnityEngine::ComponentExtensions::SafeSetActive(this->settlementPanel);
uStack_30 = 0x1816e77a6;
UnityEngine::ComponentExtensions::SafeSetActive(this->boxClickPanel);
uStack_30 = 0x1816e77b0;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9ba5);
if (bVar1 == 0) {
  x = (Object *)this->blackLoadingPanel;
  uStack_30 = 0x1836b0c77;
  bVar1 = UnityEngine::Object::op_Inequality(x,(Object *)0x0);
  if (bVar1 != 0) {
    if (x == (Object *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1836b0ca7;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x1836b0c88;
    pGVar3 = UnityEngine::Component::get_gameObject((Component *)x);
    uStack_30 = 0x1836b0c97;
    UnityEngine::GameObjectExtensions::SafeSetActive(pGVar3,0,1);
  }
  return;
}
uStack_30 = 0x1816e77d4;
pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x9ba5);
if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1816e781c;
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
if (pIVar2->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar2->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
IFix::Core::Call::PushBoolean(&CStack_58,0);
if ((VirtualMachine *)pIVar2->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar2->virtualMachine,pIVar2->methodId,&CStack_58,
             (pIVar2->anonObj != (undefined *)0x0) + 2,0);
  return;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\