
Object *x;
byte bVar1;
ILFixDynamicMethodWrapper *pIVar2;
GameObject *pGVar3;
Call *pCVar4;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1827a13d3;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x16245);
if (bVar1 == 0) {
  uStack_30 = 0x1827a13ec;
  UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelSize,0,1);
  uStack_30 = 0x1827a13fd;
  UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelAnimSequence,0,1);
  uStack_30 = 0x1827a140e;
  UnityEngine::ComponentExtensions::SafeSetActive(this->elfStarImg,0,1);
  uStack_30 = 0x1827a141f;
  UnityEngine::ComponentExtensions::SafeSetActive(this->stigmataAnimSequence,0,1);
  uStack_30 = 0x1827a1430;
  UnityEngine::ComponentExtensions::SafeSetActive(this->avatarCardAnimSequence,0,1);
  uStack_30 = 0x1827a1441;
  UnityEngine::ComponentExtensions::SafeSetActive(this->otherIconAnimSequence,0,1);
  uStack_30 = 0x1827a1452;
  UnityEngine::ComponentExtensions::SafeSetActive(this->titleAnimSequence,0,1);
  x = (Object *)this->titleText;
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
uStack_30 = 0x1827a1472;
pIVar2 = IFix::WrappersManagerImpl::GetPatch(0x16245);
if (pIVar2 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1827a148c;
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
il2cpp::codegen::raise_null_reference_exception();\