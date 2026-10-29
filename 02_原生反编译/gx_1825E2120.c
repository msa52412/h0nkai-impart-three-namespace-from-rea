
undefined *puVar1;
Object *x;
byte bVar2;
byte bVar3;
ILFixDynamicMethodWrapper *pIVar4;
GameObject *pGVar5;
Call *pCVar6;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1825e213a;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9bc2);
if (bVar2 == 0) {
  puVar1 = this->viceIconBtn;
  if (*(int *)(_DAT_189a18330 + 0xe8) == 0) {
    uStack_30 = 0x1825e2163;
    il2cpp::codegen::runtime_class_init(_DAT_189a18330);
  }
  uStack_30 = 0x1825e2179;
  bVar2 = System::String::Equals
                    (gachaUIColorType,(undefined *)**(undefined8 **)(_DAT_189a18330 + 0x28));
  uStack_30 = 0x1825e2187;
  UnityEngine::ComponentExtensions::SafeSetActive(puVar1,bVar2,1);
  puVar1 = this->effectOrangeTrans;
  uStack_30 = 0x1825e21a2;
  bVar2 = System::String::Equals
                    (gachaUIColorType,*(undefined **)(*(longlong *)(_DAT_189a18330 + 0x28) + 8));
  uStack_30 = 0x1825e21b0;
  UnityEngine::ComponentExtensions::SafeSetActive(puVar1,bVar2,1);
  x = (Object *)this->effectVioletTrans;
  uStack_30 = 0x1825e21ce;
  bVar2 = System::String::Equals
                    (gachaUIColorType,*(undefined **)(*(longlong *)(_DAT_189a18330 + 0x28) + 0x10)
                    );
  uStack_30 = 0x1836b0c77;
  bVar3 = UnityEngine::Object::op_Inequality(x,(Object *)0x0);
  if (bVar3 != 0) {
    if (x == (Object *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1836b0ca7;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x1836b0c88;
    pGVar5 = UnityEngine::Component::get_gameObject((Component *)x);
    uStack_30 = 0x1836b0c97;
    UnityEngine::GameObjectExtensions::SafeSetActive(pGVar5,bVar2,1);
  }
  return;
}
uStack_30 = 0x1825e21f5;
pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x9bc2);
if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1825e2217;
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
if (pIVar4->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar4->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
IFix::Core::Call::PushObject(&CStack_58,gachaUIColorType);
if ((VirtualMachine *)pIVar4->virtualMachine != (VirtualMachine *)0x0) {
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,&CStack_58,
             (pIVar4->anonObj != (undefined *)0x0) + 2,0);
  return;
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\