
undefined4 uVar1;
longlong *plVar2;
byte bVar3;
KeyGeneratedEventHandler *pKVar4;
LNFBAFMHDEH *this_00;
ILFixDynamicMethodWrapper *pIVar5;
Call *pCVar6;
GradientAlphaKey GStackX_10;
uint in_stack_ffffffffffffff98;
Call CStack_58;
undefined8 uStack_28;
undefined4 uStack_20;
undefined8 uStack_18;
undefined4 uStack_10;

bVar3 = IFix::WrappersManagerImpl::IsPatched(0x19a88);
if (bVar3 != 0) {
  pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x19a88);
  if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
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
  if ((VirtualMachine *)pIVar5->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar5->virtualMachine,pIVar5->methodId,&CStack_58,
               (pIVar5->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
plVar2 = (longlong *)this->dropsScroller;
pKVar4 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a15710);
KeyGeneratedEventHandler::_ctor(pKVar4,(undefined *)this,_DAT_189ad4790);
if (this->itemList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uVar1 = *(undefined4 *)(this->itemList + 0x18);
GStackX_10.alpha = 0.0;
GStackX_10.time = 0.0;
UnityEngine::GradientAlphaKey::_ctor(&GStackX_10,0.0,_DAT_187975b88);
uStack_28 = 0;
uStack_20 = 0;
func_0x000185350640(&uStack_28,GStackX_10,0);
if (plVar2 != (longlong *)0x0) {
  uStack_10 = uStack_20;
  uStack_18 = uStack_28;
  CStack_58.topWriteBack = *(undefined **)(*plVar2 + 0x1a0);
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)CONCAT44(CStack_58.evaluationStackBase._4_4_,2);
  CStack_58.argumentBase = (undefined *)((ulonglong)CStack_58.argumentBase & 0xffffffffffffff00);
  (**(code **)(*plVar2 + 0x198))
            (plVar2,pKVar4,uVar1,&uStack_18,in_stack_ffffffffffffff98 & 0xffffff00,1);
  pKVar4 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
  KeyGeneratedEventHandler::_ctor(pKVar4,(undefined *)this,_DAT_189ad4798);
  this_00 = (LNFBAFMHDEH *)il2cpp::codegen::object_new(_DAT_189a19e80);
  LNFBAFMHDEH::_ctor(this_00,(Action *)pKVar4,(undefined *)0x0,(Action *)0x0);
  this->animationManager = (undefined *)this_00;
  if (this_00 != (LNFBAFMHDEH *)0x0) {
    LNFBAFMHDEH::IPNPJLBFJPI(this_00,(Transform *)this->dropsScrollerContent);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\