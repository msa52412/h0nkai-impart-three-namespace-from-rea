
uint uVar1;
undefined8 uVar2;
MonoAvatarStar *this_00;
longlong *plVar3;
byte bVar4;
int iVar5;
longlong lVar6;
CFINMGJAHEA *this_01;
ElfMetaData *this_02;
ElfRarityMetaData *this_03;
undefined *puVar7;
undefined *arg1;
AvatarIDs *pAVar8;
AvatarMetaData *pAVar9;
TextID TVar10;
ILFixDynamicMethodWrapper *pIVar11;
Call *pCVar12;
undefined4 auStackX_10 [6];
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1825e2723;
bVar4 = IFix::WrappersManagerImpl::IsPatched(0x9bbe);
if (bVar4 != 0) {
  uStack_30 = 0x1825e274e;
  pIVar11 = IFix::WrappersManagerImpl::GetPatch(0x9bbe);
  if (pIVar11 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e2768;
    il2cpp::codegen::raise_null_reference_exception();
  }
  CStack_58.argumentBase = (undefined *)0x0;
  CStack_58.evaluationStackBase = (undefined *)0x0;
  CStack_58.managedStack = (undefined *)0x0;
  CStack_58.currentTop = (undefined *)0x0;
  CStack_58.topWriteBack = (undefined *)0x0;
  pCVar12 = IFix::Core::Call::Begin();
  CStack_58.argumentBase = pCVar12->argumentBase;
  CStack_58.evaluationStackBase = pCVar12->evaluationStackBase;
  CStack_58.managedStack = pCVar12->managedStack;
  CStack_58.currentTop = pCVar12->currentTop;
  CStack_58.topWriteBack = pCVar12->topWriteBack;
  if (pIVar11->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject(&CStack_58,pIVar11->anonObj);
  }
  IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
  if ((VirtualMachine *)pIVar11->virtualMachine != (VirtualMachine *)0x0) {
    IFix::Core::VirtualMachine::Execute
              ((VirtualMachine *)pIVar11->virtualMachine,pIVar11->methodId,&CStack_58,
               (pIVar11->anonObj != (undefined *)0x0) + 1,0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uStack_30 = 0x1825e272f;
SetMainIcon(this);
uStack_30 = 0x1825e2737;
SetupMainRarity(this);
uStack_30 = 0x1825e2343;
bVar4 = IFix::WrappersManagerImpl::IsPatched(0x9bc5);
if (bVar4 != 0) {
  uStack_30 = 0x1825e268e;
  pIVar11 = IFix::WrappersManagerImpl::GetPatch(0x9bc5);
  if (pIVar11 != (ILFixDynamicMethodWrapper *)0x0) {
    uStack_30 = 0x1825e269e;
    IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(pIVar11,(undefined *)this);
    return;
  }
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x1825e2703;
  il2cpp::codegen::raise_null_reference_exception();
}
uVar1 = *(uint *)&this->viceNumText;
uStack_30 = 0x1825e2376;
UnityEngine::ComponentExtensions::SafeSetActive(this->effectContinueTransList,uVar1 < 2,1);
if (uVar1 < 2) {
  uStack_30 = 0x1825e238c;
  bVar4 = UnityEngine::Object::op_Inequality
                    ((Object *)this->effectContinueTransList,(Object *)0x0);
  if (bVar4 != 0) {
    if (*(int *)&this->viceNumText == 0) {
      if (*(longlong *)&this->mainItemType == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26d3;
        il2cpp::codegen::raise_null_reference_exception();
      }
      iVar5 = *(int *)(*(longlong *)&this->mainItemType + 0x14);
      if (*(int *)(_DAT_189a15800 + 0xe8) == 0) {
        uStack_30 = 0x1825e2498;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x1825e249f;
      pAVar8 = ExcelMeta::AvatarMetaDataReaderExtend::GetAvatarIDsByKey(iVar5);
      if (pAVar8 == (AvatarIDs *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26cd;
        il2cpp::codegen::raise_null_reference_exception();
      }
      iVar5 = pAVar8->avatarID;
      if (*(int *)(_DAT_1899f1f78 + 0xe8) == 0) {
        uStack_30 = 0x1825e24c0;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x1825e24c7;
      pAVar9 = ExcelMeta::KPPOOEBNLCJ::IIGJACLGBNB(iVar5);
      if (pAVar9 == (AvatarMetaData *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26c7;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e24d8;
      iVar5 = ExcelMeta::AvatarMetaData::get_unlockStar(pAVar9);
      if ((MonoAvatarStar *)this->effectContinueTransList == (MonoAvatarStar *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26c1;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e24ef;
      MonoAvatarStar::SetupView((MonoAvatarStar *)this->effectContinueTransList,iVar5);
    }
    else if (*(int *)&this->viceNumText == 1) {
      uVar2._0_4_ = this->mainItemType;
      uVar2._4_4_ = this->newDisplayType;
      uStack_30 = 0x1825e23c1;
      lVar6 = func_0x000180257760(uVar2,_DAT_189a18310);
      if (lVar6 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26bb;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e23d9;
      this_01 = (CFINMGJAHEA *)func_0x000180257760(uVar2,_DAT_189a18310);
      uStack_30 = 0x1825e23e1;
      iVar5 = CFINMGJAHEA::LCADOKEIFEG(this_01);
      if (*(int *)(_DAT_1899f0960 + 0xe8) == 0) {
        uStack_30 = 0x1825e23f8;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x1825e23ff;
      this_02 = ExcelMeta::DGEPKJFENJF::AMOMNBIPOIO(iVar5);
      if (this_02 == (ElfMetaData *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26b5;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e2410;
      iVar5 = ExcelMeta::ElfMetaData::get_Rarity(this_02);
      if (*(int *)(_DAT_1899eff90 + 0xe8) == 0) {
        uStack_30 = 0x1825e2427;
        il2cpp::codegen::runtime_class_init();
      }
      uStack_30 = 0x1825e242e;
      this_03 = ExcelMeta::OBLLOHJNIOD::BOJEHBLNHIB(iVar5);
      this_00 = (MonoAvatarStar *)this->effectContinueTransList;
      if (this_03 == (ElfRarityMetaData *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26af;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e2446;
      puVar7 = ExcelMeta::ElfRarityMetaData::get_rarityImg(this_03);
      if (this_00 == (MonoAvatarStar *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1825e26a9;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x1825e245a;
      MonoAvatarStar::ForceSetImage(this_00,puVar7);
    }
  }
}
iVar5 = *(int *)&this->viceNumText;
uStack_30 = 0x1825e250c;
UnityEngine::ComponentExtensions::SafeSetActive(this->infoAvatarStar,iVar5 == 2 || iVar5 == 3,1);
if (iVar5 == 2 || iVar5 == 3) {
  uStack_30 = 0x1825e251e;
  bVar4 = UnityEngine::Object::op_Inequality((Object *)this->infoAvatarStar,(Object *)0x0);
  if (bVar4 != 0) {
    if ((MonoEquipSubStar *)this->infoAvatarStar == (MonoEquipSubStar *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1825e26d9;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x1825e253e;
    MonoEquipSubStar::SetupViewWithGetMaxRarity
              ((MonoEquipSubStar *)this->infoAvatarStar,
               *(StorageDataItemBase **)&this->mainItemType);
  }
}
if (*(int *)&this->viceNumText == 0) {
  if (*(longlong *)&this->mainItemType == 0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e26fd;
    il2cpp::codegen::raise_null_reference_exception();
  }
  iVar5 = *(int *)(*(longlong *)&this->mainItemType + 0x14);
  if (*(int *)(_DAT_189a15800 + 0xe8) == 0) {
    uStack_30 = 0x1825e25f9;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x1825e2600;
  pAVar8 = ExcelMeta::AvatarMetaDataReaderExtend::GetAvatarIDsByKey(iVar5);
  if (pAVar8 == (AvatarIDs *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e26f7;
    il2cpp::codegen::raise_null_reference_exception();
  }
  iVar5 = pAVar8->avatarID;
  if (*(int *)(_DAT_1899f1f78 + 0xe8) == 0) {
    uStack_30 = 0x1825e2621;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x1825e2628;
  pAVar9 = ExcelMeta::KPPOOEBNLCJ::IIGJACLGBNB(iVar5);
  if (pAVar9 == (AvatarMetaData *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1825e26f1;
    il2cpp::codegen::raise_null_reference_exception();
  }
  uStack_30 = 0x1825e2639;
  TVar10 = ExcelMeta::AvatarMetaData::get_fullName(pAVar9);
  uStack_30 = 0x1825e2647;
  puVar7 = (undefined *)FUN_1803c6940(_DAT_189a652d0);
  uStack_30 = 0x1825e2651;
  puVar7 = LocalizationGeneralLogic::GetText((TextID)((ulonglong)TVar10 & 0xffffffff),puVar7);
}
else {
  plVar3 = *(longlong **)&this->mainItemType;
  if (*(int *)&this->viceNumText == 5) {
    if (plVar3 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1825e26eb;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x1825e258f;
    puVar7 = (undefined *)(**(code **)(*plVar3 + 0x2f8))(plVar3,*(undefined8 *)(*plVar3 + 0x300));
    if (*(longlong *)&this->mainItemType == 0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1825e26e5;
      il2cpp::codegen::raise_null_reference_exception();
    }
    auStackX_10[0] = *(undefined4 *)(*(longlong *)&this->mainItemType + 0x28);
    uStack_30 = 0x1825e25ba;
    arg1 = (undefined *)thunk_FUN_18042cf20(_DAT_1899de3d8,auStackX_10);
    uStack_30 = 0x1825e25cc;
    puVar7 = StrUtils::Format(_DAT_189b73988,puVar7,arg1);
  }
  else {
    if (plVar3 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      uStack_30 = 0x1825e26df;
      il2cpp::codegen::raise_null_reference_exception();
    }
    uStack_30 = 0x1825e2571;
    puVar7 = (undefined *)(**(code **)(*plVar3 + 0x2f8))(plVar3,*(undefined8 *)(*plVar3 + 0x300));
  }
}
uStack_30 = 0x1825e2663;
UnityEngine::UI::TextExtensions::SafeSetText(this->infoEquipStar,puVar7,1);
uStack_30 = 0x1825e2679;
UnityEngine::UI::TextExtensions::SafeSetText(this->nameText,_DAT_189b73990,1);
return;\