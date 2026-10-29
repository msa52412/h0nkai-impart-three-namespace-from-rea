
uint uVar1;
undefined *puVar2;
longlong lVar3;
bool bVar4;
byte bVar5;
int iVar6;
StorageDataItemBase *pSVar7;
longlong lVar8;
CFINMGJAHEA *this_00;
AvatarIDs *pAVar9;
ILFixDynamicMethodWrapper *pIVar10;
Call *pCVar11;
undefined8 uVar12;
StorageDataItemBase *pSVar13;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1816e6c4a;
bVar5 = IFix::WrappersManagerImpl::IsPatched(0x9c07);
lVar3 = _DAT_189a18310;
if (bVar5 != 0) {
  uStack_30 = 0x1816e6d84;
  pIVar10 = IFix::WrappersManagerImpl::GetPatch(0x9c07);
  if (pIVar10 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1816e6db8;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar11 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar11->argumentBase;
  CStack_58.evaluationStackBase = pCVar11->evaluationStackBase;
  CStack_58.managedStack = pCVar11->managedStack;
  CStack_58.currentTop = pCVar11->currentTop;
  CStack_58.topWriteBack = pCVar11->topWriteBack;
  if (pIVar10->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar10->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)mainItem);
  if ((VirtualMachine *)pIVar10->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar10->virtualMachine,pIVar10->methodId,&CStack_58,
             (pIVar10->anonObj != (undefined *)0x0) + 2,0);
  return;
}
if (mainItem != (StorageDataItemBase *)0x0) {
  puVar2 = mainItem->__klass;
  pSVar13 = (StorageDataItemBase *)0x0;
  if (((byte)puVar2[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
     (bVar4 = true,
     *(longlong *)
      (*(longlong *)(puVar2 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8)
     != _DAT_189a15818)) {
    bVar4 = false;
  }
  pSVar7 = pSVar13;
  if (bVar4) {
    pSVar7 = mainItem;
  }
  if (pSVar7 == (StorageDataItemBase *)0x0) {
    if (((byte)puVar2[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
       (pSVar7 = (StorageDataItemBase *)0x1,
       *(longlong *)
        (*(longlong *)(puVar2 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8
        ) != _DAT_189a18310)) {
      pSVar7 = pSVar13;
    }
    if ((char)pSVar7 != '\0') {
      pSVar13 = mainItem;
    }
    if (pSVar13 != (StorageDataItemBase *)0x0) {
      puVar2 = this->resultNewElfIds;
      uStack_30 = 0x1816e6cf4;
      lVar8 = func_0x000180257760(mainItem,_DAT_189a18310);
      if (lVar8 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1816e6dac;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1816e6d08;
      this_00 = (CFINMGJAHEA *)func_0x000180257760(mainItem,lVar3);
      uStack_30 = 0x1816e6d10;
      iVar6 = CFINMGJAHEA::LCADOKEIFEG(this_00);
      if (puVar2 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1816e6da6;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1816e6d26;
      FUN_184a6a1f0(puVar2,iVar6,0);
    }
  }
  else {
    iVar6 = mainItem->uid;
    if (*(int *)(_DAT_189a15800 + 0xe8) == 0) {
      uStack_30 = 0x1816e6d4d;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x1816e6d54;
    pAVar9 = ExcelMeta::AvatarMetaDataReaderExtend::GetAvatarIDsByKey(iVar6);
    if (pAVar9 != (AvatarIDs *)0x0) {
      puVar2 = this->resultNewAvatarIds;
      if (puVar2 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1816e6db2;
        il2cpp::codegen::raise_null_reference_exception();
      }
      iVar6 = pAVar9->avatarID;
      if (*(longlong *)(puVar2 + 0x10) == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184a6a25f;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(int *)(puVar2 + 0x18) == *(int *)(*(longlong *)(puVar2 + 0x10) + 0x18)) {
        uStack_30 = 0x184a6a21a;
        FUN_184a6e030(puVar2,*(int *)(puVar2 + 0x18) + 1,0);
      }
      uVar1 = *(uint *)(puVar2 + 0x18);
      lVar3 = *(longlong *)(puVar2 + 0x10);
      *(uint *)(puVar2 + 0x18) = uVar1 + 1;
      if (lVar3 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184a6a259;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(uint *)(lVar3 + 0x18) <= uVar1) {
        uStack_30 = 0x184a6a249;
        uVar12 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184a6a253;
        il2cpp::codegen::raise_exception(uVar12,0);
      }
      *(int *)(lVar3 + 0x20 + (longlong)(int)uVar1 * 4) = iVar6;
      *(int *)(puVar2 + 0x1c) = *(int *)(puVar2 + 0x1c) + 1;
      return;
    }
  }
}
return;\