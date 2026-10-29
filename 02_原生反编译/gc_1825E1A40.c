
Animation *this_00;
longlong lVar1;
undefined *o;
byte bVar2;
AnimationClip *pAVar3;
undefined *puVar4;
AnimationState *this_01;
ILFixDynamicMethodWrapper *pIVar5;
undefined8 uVar6;
Call *pCVar7;
uint uVar8;
float fVar9;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1825e1a53;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9c1c);
if (bVar2 != 0) {
  uStack_30 = 0x1825e1a9f;
  pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x9c1c);
  if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e1abf;
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
if (*(Behaviour **)&this->enableDeliveryMsgToSonCmpt == (Behaviour *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1825e1ab9;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1825e1a67;
UnityEngine::Behaviour::set_enabled(*(Behaviour **)&this->enableDeliveryMsgToSonCmpt,1);
fVar9 = _DAT_187975b88;
*(undefined4 *)&this->getAsyncLoader = 3;
uStack_30 = 0x1825e1a81;
SetAnimationSpeed(this,fVar9);
o = _DAT_189b739a8;
CStack_58.evaluationStackBase = (undefined *)0x1825e1768;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x9c18);
if (bVar2 != 0) {
  CStack_58.evaluationStackBase = (undefined *)0x1825e18a1;
  pIVar5 = IFix::WrappersManagerImpl::GetPatch(0x9c18);
  if (pIVar5 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x1825e190d;
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
  if (pIVar5->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar5->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  IFix::Core::Call::PushObject(&CStack_58,o);
  if ((VirtualMachine *)pIVar5->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar5->virtualMachine,pIVar5->methodId,&CStack_58,
               (pIVar5->anonObj != (undefined *)0x0) + 2,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
this_00 = *(Animation **)&this->enableDeliveryMsgToSonCmpt;
if (this_00 == (Animation *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x1825e1907;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x1825e178a;
pAVar3 = UnityEngine::Animation::get_clip(this_00);
if (pAVar3 == (AnimationClip *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x1825e1901;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x1825e179b;
puVar4 = UnityEngine::Object::get_name((Object *)pAVar3);
if (this_00 == (Animation *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x1825e18fb;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x1825e17c3;
this_01 = UnityEngine::Animation::get_Item(this_00,puVar4);
fVar9 = 0.0;
CStack_58.evaluationStackBase = (undefined *)0x1825e17d1;
bVar2 = System::String::IsNullOrEmpty(o);
if (bVar2 == 0) {
  if (this_01 == (AnimationState *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x1825e18e3;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x1825e17e6;
  pAVar3 = UnityEngine::AnimationState::get_clip(this_01);
  if (pAVar3 == (AnimationClip *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x1825e18dd;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.evaluationStackBase = (undefined *)0x1825e17f7;
  puVar4 = UnityEngine::AnimationClip::get_events(pAVar3);
  uVar8 = 0;
  if (puVar4 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
    CStack_58.evaluationStackBase = (undefined *)0x1825e18d7;
    il2cpp::codegen::raise_null_reference_exception();
  }
  while( true ) {
    if ((int)*(uint *)(puVar4 + 0x18) <= (int)uVar8) break;
    if (*(uint *)(puVar4 + 0x18) <= uVar8) {
      CStack_58.evaluationStackBase = (undefined *)0x1825e18c7;
      uVar6 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x1825e18d1;
      il2cpp::codegen::raise_exception(uVar6,0);
    }
    lVar1 = *(longlong *)(puVar4 + (longlong)(int)uVar8 * 8 + 0x20);
    if (lVar1 == 0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.evaluationStackBase = (undefined *)0x1825e18c1;
      il2cpp::codegen::raise_null_reference_exception();
    }
    CStack_58.evaluationStackBase = (undefined *)0x1825e1833;
    bVar2 = System::String::Equals(*(undefined **)(lVar1 + 0x18),o);
    if (bVar2 != 0) {
      fVar9 = *(float *)(lVar1 + 0x10);
      break;
    }
    uVar8 = uVar8 + 1;
  }
}
if (this_01 == (AnimationState *)0x0) {
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x1825e18f5;
  il2cpp::codegen::raise_null_reference_exception();
}
CStack_58.evaluationStackBase = (undefined *)0x1825e1856;
UnityEngine::AnimationState::set_time(this_01,fVar9);
if (*(Animation **)&this->enableDeliveryMsgToSonCmpt != (Animation *)0x0) {
  CStack_58.evaluationStackBase = (undefined *)0x1825e1868;
  UnityEngine::Animation::Play(*(Animation **)&this->enableDeliveryMsgToSonCmpt);
  lVar1._0_1_ = this->enableDeliveryMsgToSonCmpt;
  lVar1._1_1_ = this->hasAttached;
  lVar1._2_1_ = this->turnOnOptimize;
  lVar1._3_1_ = this->pad_3B[0];
  lVar1._4_1_ = this->pad_3B[1];
  lVar1._5_1_ = this->pad_3B[2];
  lVar1._6_1_ = this->pad_3B[3];
  lVar1._7_1_ = this->pad_3B[4];
  if (lVar1 != 0) {
                  /* WARNING: Could not recover jumptable at 0x00018699c1f0. Too many branches */
                  /* WARNING: Treating indirect jump as call */
    (*_DAT_1899d9c80)();
    return;
  }
                  /* WARNING: Subroutine does not return */
  CStack_58.evaluationStackBase = (undefined *)0x1825e18e9;
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
CStack_58.evaluationStackBase = (undefined *)0x1825e18ef;
il2cpp::codegen::raise_null_reference_exception();\