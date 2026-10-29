
ParticleSystem *this_00;
byte bVar1;
Transform *pTVar2;
longlong lVar3;
ILFixDynamicMethodWrapper *this_01;
undefined8 uVar4;
uint uVar5;

bVar1 = IFix::WrappersManagerImpl::IsPatched(0x19aae);
if (bVar1 == 0) {
  lVar3._0_4_ = this->levelID;
  lVar3._4_1_ = this->pad_54[0];
  lVar3._5_1_ = this->pad_54[1];
  lVar3._6_1_ = this->pad_54[2];
  lVar3._7_1_ = this->pad_54[3];
  if (lVar3 != 0) {
    bVar1 = CanSplit(this);
    if (bVar1 != 0) {
      SetAfterSplitView(this);
    }
    if (isRareDrop != 0) {
      pTVar2 = UnityEngine::Component::get_transform((Component *)this);
      UnityEngine::TransformExtensions::SafeShowUINode(pTVar2,_DAT_189b73a48,1);
      pTVar2 = UnityEngine::Component::get_transform((Component *)this);
      lVar3 = UnityEngine::Transform::Find(pTVar2,_DAT_189b73a48,1);
      if (lVar3 == 0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      lVar3 = FUN_183978f30(lVar3,_DAT_189a9b110);
      uVar5 = 0;
      if (lVar3 == 0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      while( true ) {
        if ((int)*(uint *)(lVar3 + 0x18) <= (int)uVar5) break;
        if (*(uint *)(lVar3 + 0x18) <= uVar5) {
          uVar4 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
          il2cpp::codegen::raise_exception(uVar4,0);
        }
        this_00 = *(ParticleSystem **)(lVar3 + 0x20 + (longlong)(int)uVar5 * 8);
        if (this_00 == (ParticleSystem *)0x0) {
                  /* WARNING: Subroutine does not return */
          il2cpp::codegen::raise_null_reference_exception();
        }
        UnityEngine::ParticleSystem::Play(this_00);
        uVar5 = uVar5 + 1;
      }
    }
  }
}
else {
  this_01 = IFix::WrappersManagerImpl::GetPatch(0x19aae);
  if (this_01 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_12(this_01,(undefined *)this,isRareDrop);
}
return;\