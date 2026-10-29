
byte bVar1;
Transform *pTVar2;
ILFixDynamicMethodWrapper *pIVar3;

bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9bbc);
if (bVar1 == 0) {
  *(StorageDataItemBase **)&this->isMainItemRare = viceItem;
  this->viceItem = onIconBtnClick;
  this->onIconBtnClick = (undefined *)getAsyncLoader;
  *(uint *)((longlong)&this->viceNumText + 4) = newDisplayType;
  *(StorageDataItemBase **)&this->mainItemType = mainItem;
  *(byte *)&this->mainItem = isMainItemRare;
  pTVar2 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar2 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar2 = UnityEngine::Transform::get_parent(pTVar2);
  UnityEngine::ComponentExtensions::SafeSetActive(pTVar2,1);
  CalMainItemType(this);
  bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9bbe);
  if (bVar1 == 0) {
    SetMainIcon(this);
    SetupMainRarity(this);
    SetMainInfo(this);
  }
  else {
    pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9bbe);
    if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(pIVar3,(undefined *)this);
  }
  bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9bc8);
  if (bVar1 == 0) {
    UnityEngine::ComponentExtensions::SafeSetActive(this->effectBlueTrans,0,1);
  }
  else {
    pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9bc8);
    if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    IFix::ILFixDynamicMethodWrapper::Gen_Wrap_12(pIVar3,(undefined *)this,0);
  }
  SetOnceEffectActive(this,1);
  SetContinueEffectActive(this,1);
  SetViceItem(this);
  MonoBaseUIComponent::SafeSetActive((MonoBaseUIComponent *)this,0);
  if (*(Behaviour **)&this->enableDeliveryMsgToSonCmpt == (Behaviour *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  UnityEngine::Behaviour::set_enabled(*(Behaviour **)&this->enableDeliveryMsgToSonCmpt,0);
}
else {
  pIVar3 = IFix::WrappersManagerImpl::GetPatch(0x9bbc);
  if (pIVar3 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_4476
            ((ILFixDynamicMethodWrapper_57479 *)pIVar3,(undefined *)this,newDisplayType,
             (undefined *)mainItem,isMainItemRare,(undefined *)viceItem,onIconBtnClick,
             (undefined *)getAsyncLoader);
}
return;\