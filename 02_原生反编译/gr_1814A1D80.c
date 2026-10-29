
undefined *puVar1;
StorageDataItemBase *itemData;
byte bVar2;
MonoLevelDropIconButton *this_00;
KeyGeneratedEventHandler *this_01;
longlong lVar3;
ILFixDynamicMethodWrapper *pIVar4;
Call *pCVar5;
undefined *puStack_58;
undefined *puStack_50;

bVar2 = IFix::WrappersManagerImpl::IsPatched(0x19a89);
if (bVar2 != 0) {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x19a89);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  puStack_58 = (undefined *)0x0;
  puStack_50 = (undefined *)0x0;
  pCVar5 = IFix::Core::Call::Begin();
  puStack_58 = pCVar5->argumentBase;
  puStack_50 = pCVar5->evaluationStackBase;
  if (pIVar4->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject((Call *)&puStack_58,pIVar4->anonObj);
  }
  IFix::Core::Call::PushObject((Call *)&puStack_58,(undefined *)this);
  IFix::Core::Call::PushObject((Call *)&puStack_58,(undefined *)trans);
  IFix::Core::Call::PushInt32((Call *)&puStack_58,index);
  if ((VirtualMachine *)pIVar4->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,(Call *)&puStack_58,
               (pIVar4->anonObj != (undefined *)0x0) + 3,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
puVar1 = this->itemList;
if (puVar1 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(uint *)(puVar1 + 0x18) <= (uint)index) {
  System::ThrowHelper::ThrowArgumentOutOfRangeException();
}
itemData = *(StorageDataItemBase **)(*(longlong *)(puVar1 + 0x10) + 0x20 + (longlong)index * 8);
this_00 = (MonoLevelDropIconButton *)FUN_183997ac0(trans,0,0,1);
if (this_00 != (MonoLevelDropIconButton *)0x0) {
  MonoLevelDropIconButton::SetupCanvasAlpha(this_00,0.0);
  this_01 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a15820);
  KeyGeneratedEventHandler::_ctor(this_01,(undefined *)this,_DAT_189ad47a0);
  MonoLevelDropIconButton::SetupView
            (this_00,itemData,(DropItemButtonClickCallBack *)this_01,1,1,0,0,0,0,0,_DAT_189b4a238)
  ;
  MonoLevelDropIconButton::ShowRecyleMarkIfRecycleAndNotNew(this_00,1);
  MonoLevelDropIconButton::SetTransparent(this_00);
  if (trans == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  lVar3 = FUN_183978ec0(trans,_DAT_189aa0948);
  if (lVar3 != 0) {
    *(undefined8 *)(lVar3 + 0x28) = _DAT_189b7e3d8;
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
                  /* WARNING: Subroutine does not return */
il2cpp::codegen::raise_null_reference_exception();\