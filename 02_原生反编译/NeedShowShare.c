
bool bVar1;
undefined8 uVar2;
undefined8 uVar3;
byte bVar4;
char cVar5;
int iVar6;
undefined *puVar7;
StorageDataItemBase *pSVar8;
longlong lVar9;
AvatarIDs *pAVar10;
AvatarModule *this_00;
AvatarDataItem *pAVar11;
ILFixDynamicMethodWrapper *pIVar12;
Call *pCVar13;
int iVar14;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x181b2f4ca;
bVar4 = IFix::WrappersManagerImpl::IsPatched(0x112e7);
if (bVar4 != 0) {
  uStack_30 = 0x181b2f710;
  pIVar12 = IFix::WrappersManagerImpl::GetPatch(0x112e7);
  if (pIVar12 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x181b2f762;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar13 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar13->argumentBase;
  CStack_58.evaluationStackBase = pCVar13->evaluationStackBase;
  CStack_58.managedStack = pCVar13->managedStack;
  CStack_58.currentTop = pCVar13->currentTop;
  CStack_58.topWriteBack = pCVar13->topWriteBack;
  if (pIVar12->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar12->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)storageItem);
  if ((VirtualMachine *)pIVar12->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar12->virtualMachine,pIVar12->methodId,&CStack_58,
               (pIVar12->anonObj != (undefined *)0x0) + 2,0);
    bVar4 = IFix::Core::Call::GetBoolean(&CStack_58,0);
    return bVar4;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
  uStack_30 = 0x181b2f4e7;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x181b2f4ec;
puVar7 = ExcelMeta::ConstValueDataReaderExtend::get_ShareUniqueItemID();
if (storageItem == (StorageDataItemBase *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x181b2f75c;
  il2cpp::codegen::raise_null_reference_exception();
}
if (puVar7 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x181b2f756;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x181b2f50c;
cVar5 = FUN_184a6d630(puVar7,storageItem->uid,0);
uVar3 = _DAT_189a15a58;
if (cVar5 != '\0') {
  return 1;
}
if (((byte)storageItem->__klass[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
   (bVar1 = true,
   *(longlong *)
    (*(longlong *)(storageItem->__klass + 0x50) +
    (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8) != _DAT_189a15818)) {
  bVar1 = false;
}
pSVar8 = (StorageDataItemBase *)0x0;
if (bVar1) {
  pSVar8 = storageItem;
}
if (pSVar8 == (StorageDataItemBase *)0x0) {
  uStack_30 = 0x181b2f570;
  lVar9 = func_0x000180257760(storageItem,_DAT_189a15a58);
  uVar2 = _DAT_189a15a50;
  if (lVar9 == 0) {
    uStack_30 = 0x181b2f58b;
    lVar9 = func_0x000180257760(storageItem,_DAT_189a15a50);
    uVar3 = _DAT_189a18310;
    if (lVar9 == 0) {
      uStack_30 = 0x181b2f5a2;
      lVar9 = func_0x000180257760(storageItem,_DAT_189a18310);
      if (lVar9 == 0) {
        return 0;
      }
      uStack_30 = 0x181b2f5c2;
      lVar9 = func_0x000180257760(storageItem,uVar3);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x181b2f732;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x181b2f5d6;
      lVar9 = func_0x000180257760(storageItem,uVar3);
      iVar14 = *(int *)(lVar9 + 0x18);
      if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
        uStack_30 = 0x181b2f5ed;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x181b2f5f2;
      iVar6 = ExcelMeta::ConstValueDataReaderExtend::get_ShareElfBaseRarity();
    }
    else {
      uStack_30 = 0x181b2f60f;
      lVar9 = func_0x000180257760(storageItem,uVar2);
      if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x181b2f738;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x181b2f623;
      lVar9 = func_0x000180257760(storageItem,uVar2);
      iVar14 = *(int *)(lVar9 + 0x18);
      if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
        uStack_30 = 0x181b2f63a;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x181b2f63f;
      iVar6 = ExcelMeta::ConstValueDataReaderExtend::get_ShareEquipmentBaseRarity();
    }
  }
  else {
    uStack_30 = 0x181b2f649;
    lVar9 = func_0x000180257760(storageItem,uVar3);
    if (lVar9 == 0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x181b2f73e;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x181b2f65d;
    lVar9 = func_0x000180257760(storageItem,uVar3);
    iVar14 = *(int *)(lVar9 + 0x18);
    if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
      uStack_30 = 0x181b2f674;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x181b2f679;
    iVar6 = ExcelMeta::ConstValueDataReaderExtend::get_ShareStigmataBaseRarity();
  }
  return iVar6 <= iVar14;
}
iVar14 = storageItem->uid;
if (*(int *)(_DAT_189a15800 + 0xe8) == 0) {
  uStack_30 = 0x181b2f695;
  il2cpp::codegen::runtime_class_init();
}
uStack_30 = 0x181b2f69c;
pAVar10 = ExcelMeta::AvatarMetaDataReaderExtend::GetAvatarIDsByKey(iVar14);
uStack_30 = 0x181b2f6ab;
this_00 = (AvatarModule *)FUN_180261460(_DAT_189a988c8);
if (pAVar10 == (AvatarIDs *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x181b2f750;
  il2cpp::codegen::raise_null_reference_exception();
}
if (this_00 == (AvatarModule *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x181b2f74a;
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x181b2f6c8;
pAVar11 = AvatarModule::TryGetAvatarByID(this_00,pAVar10->avatarID);
if (pAVar11 != (AvatarDataItem *)0x0) {
  iVar14 = pAVar11->VirtualGroupID;
  if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
    uStack_30 = 0x181b2f6e4;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x181b2f6e9;
  iVar6 = ExcelMeta::ConstValueDataReaderExtend::get_ShareAvatarBaseUnlockStar();
  return iVar6 <= iVar14;
}
                  /* WARNING: Subroutine does not return */
uStack_30 = 0x181b2f744;
il2cpp::codegen::raise_null_reference_exception();\