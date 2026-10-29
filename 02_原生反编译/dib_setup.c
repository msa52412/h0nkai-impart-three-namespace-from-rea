
undefined *o;
byte bVar1;
byte bVar2;
byte bVar3;
MJOMKLJCHND *this_00;
undefined *value;
ILFixDynamicMethodWrapper *pIVar4;
Transform *pTVar5;
GameObject *pGVar6;
PlayerHeadDataItem *pPVar7;
undefined8 uVar8;
undefined *puVar9;
longlong *plVar10;
Color *pCVar11;
undefined8 uVar12;
PlayerHeadDataItem *pPVar13;
longlong lVar14;
PlayerHeadDataItem *pPVar15;
PlayerHeadDataItem *pPVar16;
Call *pCVar17;
char cVar18;
PlayerHeadDataItem *pPVar19;
int iVar20;
bool value_00;
undefined *puStack_38;
undefined8 uStack_30;

bVar1 = IFix::WrappersManagerImpl::IsPatched(0x12e0a);
if (bVar1 != 0) {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x12e0a);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_9002
            ((ILFixDynamicMethodWrapper_57479 *)pIVar4,(undefined *)this,(undefined *)itemData,
             (undefined *)callBack,showDesc,showNewIcon,isGrey,hideBg,hasGot,
             showLevelDropRestriction,isUp,hasGotTextMap);
  return;
}
if (*(char *)((longlong)&this->callBack + 3) == '\0') {
  pTVar5 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b74618);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
  if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  bVar1 = UnityEngine::GameObject::get_activeSelf(pGVar6);
  *(byte *)((longlong)&this->callBack + 2) = bVar1;
  *(undefined1 *)((longlong)&this->callBack + 3) = 1;
}
Clear(this);
CacheUI(this);
*(byte *)&this->callBack = hideBg;
*(byte *)((longlong)&this->callBack + 1) = isGrey;
*(byte *)((longlong)&this->callBack + 4) = hasGot;
*(byte *)&this->itemIconCommonBGSpritePath = isUp;
*(undefined **)&this->hideBg = hasGotTextMap;
*(StorageDataItemBase **)&this->levelID = itemData;
this->dropItem = (undefined *)callBack;
*(byte *)((longlong)&this->recycleMark + 2) = showNewIcon;
SetupFrame(this);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b74658);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
pPVar19 = (PlayerHeadDataItem *)0x0;
cVar18 = '\x01';
bVar1 = 0;
pPVar7 = pPVar19;
if (itemData == (StorageDataItemBase *)0x0) {
LAB_182cc3e2d:
  value_00 = pPVar7 != (PlayerHeadDataItem *)0x0;
}
else {
  puVar9 = itemData->__klass;
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a70 + 0x132)) ||
     (bVar2 = 1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15a70 + 0x132) - 1) * 8)
     != _DAT_189a15a70)) {
    bVar2 = bVar1;
  }
  pPVar13 = pPVar19;
  if (bVar2 != 0) {
    pPVar13 = (PlayerHeadDataItem *)itemData;
  }
  if (pPVar13 == (PlayerHeadDataItem *)0x0) {
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a18338 + 0x132)) ||
       (bVar2 = 1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18338 + 0x132) - 1) * 8
        ) != _DAT_189a18338)) {
      bVar2 = bVar1;
    }
    if (bVar2 != 0) {
      pPVar7 = (PlayerHeadDataItem *)itemData;
    }
    goto LAB_182cc3e2d;
  }
  value_00 = true;
}
if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
UnityEngine::GameObject::SetActive(pGVar6,value_00);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b731d0);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uVar8 = FUN_183978ec0(pTVar5,_DAT_189a6dd70);
if (itemData == (StorageDataItemBase *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
puVar9 = StorageDataItemBase::get_ItemRarityBGImgPath(itemData);
UnityEngine::UI::ImageExtensions::SafeSetSprite(uVar8,puVar9,1);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b731d0);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
plVar10 = (longlong *)FUN_183978ec0(pTVar5,_DAT_189a6dd70);
pCVar11 = UnityEngine::Color::get_white();
if (plVar10 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
puStack_38 = *(undefined **)pCVar11;
uStack_30._0_4_ = pCVar11->b;
uStack_30._4_4_ = pCVar11->a;
(**(code **)(*plVar10 + 0x2b8))(plVar10,&puStack_38,*(undefined8 *)(*plVar10 + 0x2c0));
TryShowCustomItemReachMaxNumTip(this,itemData->uid);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b731d8);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uVar8 = FUN_183978ec0(pTVar5,_DAT_189a6dd70);
plVar10 = *(longlong **)&this->levelID;
if (plVar10 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
uVar12 = (**(code **)(*plVar10 + 0x1f8))(plVar10,*(undefined8 *)(*plVar10 + 0x200));
UnityEngine::UI::ImageExtensions::SafeSetSprite(uVar8,uVar12,1);
puVar9 = itemData->__klass;
if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a1afb8 + 0x132)) ||
   (bVar2 = 1,
   *(longlong *)
    (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a1afb8 + 0x132) - 1) * 8) !=
   _DAT_189a1afb8)) {
  bVar2 = bVar1;
}
pPVar7 = pPVar19;
if (bVar2 != 0) {
  pPVar7 = (PlayerHeadDataItem *)itemData;
}
if (pPVar7 == (PlayerHeadDataItem *)0x0) {
  pTVar5 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b731d8);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  uVar8 = FUN_183978ec0(pTVar5,_DAT_189a6dd70);
  UnityEngine::UI::ImageExtensions::SafeSetMaterial(uVar8,0,1);
}
else {
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a1afb8 + 0x132)) ||
     (pPVar7 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a1afb8 + 0x132) - 1) * 8)
     != _DAT_189a1afb8)) {
    pPVar7 = pPVar19;
  }
  pPVar13 = pPVar19;
  if ((char)pPVar7 != '\0') {
    pPVar13 = (PlayerHeadDataItem *)itemData;
  }
  if (pPVar13 == (PlayerHeadDataItem *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a1afb8 + 0x132)) ||
     (bVar2 = 1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a1afb8 + 0x132) - 1) * 8)
     != _DAT_189a1afb8)) {
    bVar2 = bVar1;
  }
  pPVar7 = pPVar19;
  if (bVar2 != 0) {
    pPVar7 = (PlayerHeadDataItem *)itemData;
  }
  puVar9 = PlayerHeadDataItem::GetBGMaterialPath(pPVar7);
  pTVar5 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b731d8);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  uVar8 = FUN_183978ec0(pTVar5,_DAT_189a6dd70);
  UnityEngine::UI::ImageExtensions::SafeSetMaterialByPath(uVar8,puVar9,1);
}
SetupRarityView(this,showDesc);
SetupStigmataTypeIcon(this);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b56f30);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
UnityEngine::GameObject::SetActive(pGVar6,showDesc);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b79e98);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
UnityEngine::GameObject::SetActive(pGVar6,showDesc);
if (*(longlong *)&this->levelID == 0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
puVar9 = (undefined *)System::Int32::ToString((StringKey *)(*(longlong *)&this->levelID + 0x28));
puVar9 = System::String::Concat(_DAT_189b75660,puVar9);
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
if (pPVar7 == (PlayerHeadDataItem *)0x0) {
LAB_182cc41e4:
  if (pPVar7 != (PlayerHeadDataItem *)0x0) {
    if (((byte)pPVar7->__klass[0x132] < *(byte *)(_DAT_189a15a58 + 0x132)) ||
       (pPVar13 = (PlayerHeadDataItem *)0x1,
       *(longlong *)
        (*(longlong *)(pPVar7->__klass + 0x50) +
        (longlong)(int)(*(byte *)(_DAT_189a15a58 + 0x132) - 1) * 8) != _DAT_189a15a58)) {
      pPVar13 = pPVar19;
    }
    pPVar16 = pPVar19;
    if ((char)pPVar13 != '\0') {
      pPVar16 = pPVar7;
    }
    if (pPVar16 != (PlayerHeadDataItem *)0x0) goto LAB_182cc422b;
  }
  lVar14 = func_0x000180257760(pPVar7,_DAT_189a15818);
  if (lVar14 == 0) {
    pTVar5 = UnityEngine::Component::get_transform((Component *)this);
    if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b74618);
    if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    plVar10 = (longlong *)FUN_183978ec0(pTVar5,_DAT_189a6fa28);
    if (plVar10 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
  }
  else {
    pTVar5 = UnityEngine::Component::get_transform((Component *)this);
    if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b74618);
    if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    plVar10 = (longlong *)FUN_183978ec0(pTVar5,_DAT_189a6fa28);
    puVar9 = _DAT_189b4a238;
    if (plVar10 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
  }
}
else {
  if (((byte)pPVar7->__klass[0x132] < *(byte *)(_DAT_189a15a50 + 0x132)) ||
     (pPVar13 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(pPVar7->__klass + 0x50) +
      (longlong)(int)(*(byte *)(_DAT_189a15a50 + 0x132) - 1) * 8) != _DAT_189a15a50)) {
    pPVar13 = pPVar19;
  }
  pPVar16 = pPVar19;
  if ((char)pPVar13 != '\0') {
    pPVar16 = pPVar7;
  }
  if (pPVar16 == (PlayerHeadDataItem *)0x0) goto LAB_182cc41e4;
LAB_182cc422b:
  if (pPVar7 == (PlayerHeadDataItem *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  puVar9 = (undefined *)System::Int32::ToString((StringKey *)&pPVar7->rarity);
  puVar9 = System::String::Concat(_DAT_189b83998,puVar9);
  pTVar5 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b74618);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  plVar10 = (longlong *)FUN_183978ec0(pTVar5,_DAT_189a6fa28);
  if (plVar10 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
}
(**(code **)(*plVar10 + 0x5f8))(plVar10,puVar9,*(undefined8 *)(*plVar10 + 0x600));
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189ba9b08);
bVar2 = UnityEngine::Object::op_Inequality((Object *)pTVar5,(Object *)0x0);
if (bVar2 != 0) {
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
  if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  UnityEngine::GameObject::SetActive(pGVar6,0);
}
lVar14 = *_DAT_189a98b00;
if (*(char *)(lVar14 + 0x136) == '\0') {
  FUN_18043e4c0(lVar14);
}
lVar14 = **(longlong **)(lVar14 + 0x90);
if (*(char *)(lVar14 + 0x136) == '\0') {
  FUN_18043e4c0(lVar14);
}
if (*(longlong *)&this->levelID == 0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if ((StorageModule *)**(undefined8 **)(lVar14 + 0x28) == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
bVar2 = StorageModule::IsItemNew
                  ((StorageModule *)**(undefined8 **)(lVar14 + 0x28),
                   *(int *)(*(longlong *)&this->levelID + 0x14));
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
pPVar13 = (PlayerHeadDataItem *)(ulonglong)bVar2;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  if (((byte)pPVar7->__klass[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
     (pPVar16 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(pPVar7->__klass + 0x50) +
      (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8) != _DAT_189a15818)) {
    pPVar16 = pPVar19;
  }
  pPVar15 = pPVar19;
  if ((char)pPVar16 != '\0') {
    pPVar15 = pPVar7;
  }
  if (pPVar15 != (PlayerHeadDataItem *)0x0) {
    if (pPVar7 == (PlayerHeadDataItem *)0x0) {
LAB_182cc4b3a:
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    puVar9 = pPVar7->__klass;
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
       (pPVar13 = (PlayerHeadDataItem *)0x1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8
        ) != _DAT_189a15818)) {
      pPVar13 = pPVar19;
    }
    pPVar16 = pPVar19;
    if ((char)pPVar13 != '\0') {
      pPVar16 = pPVar7;
    }
    if (pPVar16 == (PlayerHeadDataItem *)0x0) goto LAB_182cc4b3a;
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15818 + 0x132)) ||
       (bVar2 = 1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15818 + 0x132) - 1) * 8
        ) != _DAT_189a15818)) {
      bVar2 = bVar1;
    }
    pPVar13 = pPVar19;
    if (bVar2 != 0) {
      pPVar13 = pPVar7;
    }
    bVar2 = AvatarCardDataItem::IsSplite((AvatarCardDataItem *)pPVar13);
    pPVar13 = (PlayerHeadDataItem *)(ulonglong)(bVar2 == 0);
  }
}
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  puVar9 = pPVar7->__klass;
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
     (pPVar16 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8)
     != _DAT_189a18310)) {
    pPVar16 = pPVar19;
  }
  pPVar15 = pPVar19;
  if ((char)pPVar16 != '\0') {
    pPVar15 = pPVar7;
  }
  if (pPVar15 != (PlayerHeadDataItem *)0x0) {
    if (pPVar7 == (PlayerHeadDataItem *)0x0) {
LAB_182cc4b40:
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
       (pPVar13 = (PlayerHeadDataItem *)0x1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8
        ) != _DAT_189a18310)) {
      pPVar13 = pPVar19;
    }
    pPVar16 = pPVar19;
    if ((char)pPVar13 != '\0') {
      pPVar16 = pPVar7;
    }
    if (pPVar16 == (PlayerHeadDataItem *)0x0) goto LAB_182cc4b40;
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
       (bVar2 = 1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8
        ) != _DAT_189a18310)) {
      bVar2 = bVar1;
    }
    pPVar13 = pPVar19;
    if (bVar2 != 0) {
      pPVar13 = pPVar7;
    }
    bVar2 = CFINMGJAHEA::LJBNHOFKAMN((CFINMGJAHEA *)pPVar13);
    pPVar13 = (PlayerHeadDataItem *)(ulonglong)(bVar2 == 0);
  }
}
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  puVar9 = pPVar7->__klass;
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a70 + 0x132)) ||
     (pPVar16 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15a70 + 0x132) - 1) * 8)
     != _DAT_189a15a70)) {
    pPVar16 = pPVar19;
  }
  pPVar15 = pPVar19;
  if ((char)pPVar16 != '\0') {
    pPVar15 = pPVar7;
  }
  if (pPVar15 != (PlayerHeadDataItem *)0x0) {
    if (pPVar7 == (PlayerHeadDataItem *)0x0) {
LAB_182cc4b46:
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a70 + 0x132)) ||
       (pPVar16 = (PlayerHeadDataItem *)0x1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15a70 + 0x132) - 1) * 8
        ) != _DAT_189a15a70)) {
      pPVar16 = pPVar19;
    }
    pPVar15 = pPVar19;
    if ((char)pPVar16 != '\0') {
      pPVar15 = pPVar7;
    }
    if (pPVar15 == (PlayerHeadDataItem *)0x0) goto LAB_182cc4b46;
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a70 + 0x132)) ||
       (bVar2 = 1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15a70 + 0x132) - 1) * 8
        ) != _DAT_189a15a70)) {
      bVar2 = bVar1;
    }
    pPVar16 = pPVar19;
    if (bVar2 != 0) {
      pPVar16 = pPVar7;
    }
    bVar2 = AvatarFragmentDataItem::IsSplite((AvatarFragmentDataItem *)pPVar16);
    if (bVar2 != 0) {
      pPVar13 = (PlayerHeadDataItem *)0x0;
    }
  }
}
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  puVar9 = pPVar7->__klass;
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a182e8 + 0x132)) ||
     (pPVar16 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a182e8 + 0x132) - 1) * 8)
     != _DAT_189a182e8)) {
    pPVar16 = pPVar19;
  }
  pPVar15 = pPVar19;
  if ((char)pPVar16 != '\0') {
    pPVar15 = pPVar7;
  }
  if (pPVar15 != (PlayerHeadDataItem *)0x0) {
    if (pPVar7 == (PlayerHeadDataItem *)0x0) {
LAB_182cc4b4c:
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a182e8 + 0x132)) ||
       (pPVar16 = (PlayerHeadDataItem *)0x1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a182e8 + 0x132) - 1) * 8
        ) != _DAT_189a182e8)) {
      pPVar16 = pPVar19;
    }
    pPVar15 = pPVar19;
    if ((char)pPVar16 != '\0') {
      pPVar15 = pPVar7;
    }
    if (pPVar15 == (PlayerHeadDataItem *)0x0) goto LAB_182cc4b4c;
    if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a182e8 + 0x132)) ||
       (bVar2 = 1,
       *(longlong *)
        (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a182e8 + 0x132) - 1) * 8
        ) != _DAT_189a182e8)) {
      bVar2 = bVar1;
    }
    pPVar16 = pPVar19;
    if (bVar2 != 0) {
      pPVar16 = pPVar7;
    }
    bVar2 = MaterialDataItem::IsSplite((MaterialDataItem *)pPVar16);
    if (bVar2 != 0) {
      pPVar13 = pPVar19;
    }
  }
}
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
pPVar16 = pPVar19;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  if (((byte)pPVar7->__klass[0x132] < *(byte *)(_DAT_189a2b150 + 0x132)) ||
     (bVar2 = 1,
     *(longlong *)
      (*(longlong *)(pPVar7->__klass + 0x50) +
      (longlong)(int)(*(byte *)(_DAT_189a2b150 + 0x132) - 1) * 8) != _DAT_189a2b150)) {
    bVar2 = bVar1;
  }
  if (bVar2 != 0) {
    pPVar16 = pPVar7;
  }
}
uVar8._0_4_ = this->OffsetOfInstanceIDInCPlusPlusObject;
uVar8._4_1_ = this->pad_1C[0];
uVar8._5_1_ = this->pad_1C[1];
uVar8._6_1_ = this->pad_1C[2];
uVar8._7_1_ = this->pad_1C[3];
bVar2 = bVar1;
if (pPVar16 == (PlayerHeadDataItem *)0x0) {
  bVar2 = (byte)pPVar13;
}
bVar2 = bVar2 & showNewIcon;
UnityEngine::ComponentExtensions::SafeSetActive(uVar8,bVar2,1);
if (bVar2 != 0) {
  lVar14 = *_DAT_189a98b00;
  if (*(char *)(lVar14 + 0x136) == '\0') {
    FUN_18043e4c0(lVar14);
  }
  lVar14 = **(longlong **)(lVar14 + 0x90);
  if (*(char *)(lVar14 + 0x136) == '\0') {
    FUN_18043e4c0(lVar14);
  }
  if (*(longlong *)&this->levelID == 0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  if ((StorageModule *)**(undefined8 **)(lVar14 + 0x28) == (StorageModule *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  StorageModule::RecordNewItem
            ((StorageModule *)**(undefined8 **)(lVar14 + 0x28),
             *(int *)(*(longlong *)&this->levelID + 0x14));
}
pPVar7 = *(PlayerHeadDataItem **)&this->levelID;
if (pPVar7 != (PlayerHeadDataItem *)0x0) {
  puVar9 = pPVar7->__klass;
  if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a58 + 0x132)) ||
     (pPVar13 = (PlayerHeadDataItem *)0x1,
     *(longlong *)
      (*(longlong *)(puVar9 + 0x50) + (longlong)(int)(*(byte *)(_DAT_189a15a58 + 0x132) - 1) * 8)
     != _DAT_189a15a58)) {
    pPVar13 = pPVar19;
  }
  pPVar16 = pPVar19;
  if ((char)pPVar13 != '\0') {
    pPVar16 = pPVar7;
  }
  if (pPVar16 != (PlayerHeadDataItem *)0x0) {
    if (pPVar7 != (PlayerHeadDataItem *)0x0) {
      if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a58 + 0x132)) ||
         (pPVar13 = (PlayerHeadDataItem *)0x1,
         *(longlong *)
          (*(longlong *)(puVar9 + 0x50) +
          (longlong)(int)(*(byte *)(_DAT_189a15a58 + 0x132) - 1) * 8) != _DAT_189a15a58)) {
        pPVar13 = pPVar19;
      }
      pPVar16 = pPVar19;
      if ((char)pPVar13 != '\0') {
        pPVar16 = pPVar7;
      }
      if (pPVar16 != (PlayerHeadDataItem *)0x0) {
        if (((byte)puVar9[0x132] < *(byte *)(_DAT_189a15a58 + 0x132)) ||
           (bVar3 = 1,
           *(longlong *)
            (*(longlong *)(puVar9 + 0x50) +
            (longlong)(int)(*(byte *)(_DAT_189a15a58 + 0x132) - 1) * 8) != _DAT_189a15a58)) {
          bVar3 = bVar1;
        }
        if (bVar3 != 0) {
          pPVar19 = pPVar7;
        }
        SetupStigmataAffixView(this,(byte)(pPVar19->EndTime_k_BackingField).DaysPerYear);
        goto LAB_182cc48c4;
      }
    }
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
}
LAB_182cc48c4:
if (hideBg != 0) {
  pTVar5 = UnityEngine::Component::get_transform((Component *)this);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b56f30);
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
  if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  UnityEngine::GameObject::SetActive(pGVar6,0);
}
if (*(char *)((longlong)&this->callBack + 1) != '\0') {
  SetItemGrey(this);
}
SetItemHasGot(this,*(byte *)((longlong)&this->callBack + 4));
SetItemUp(this);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
pTVar5 = UnityEngine::Transform::Find(pTVar5,_DAT_189b694f0);
bVar1 = UnityEngine::Object::op_Inequality((Object *)pTVar5,(Object *)0x0);
if (bVar1 != 0) {
  if (pTVar5 == (Transform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pGVar6 = UnityEngine::Component::get_gameObject((Component *)pTVar5);
  if (*(char *)&this->recycleMark == '\0') {
    cVar18 = *(char *)((longlong)&this->recycleMark + 1);
  }
  if (pGVar6 == (GameObject *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  UnityEngine::GameObject::SetActive(pGVar6,cVar18 != '\0');
}
ShowLevelDropRestriction(this,showLevelDropRestriction,bVar2);
pTVar5 = UnityEngine::Component::get_transform((Component *)this);
if (*(longlong *)&this->levelID == 0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
iVar20 = *(int *)(*(longlong *)&this->levelID + 0x14);
if (*(int *)(_DAT_189a15438 + 0xe8) == 0) {
  il2cpp::codegen::runtime_class_init();
}
UIUtil::SetupPicBGByItemID(pTVar5,_DAT_189ba9b10,iVar20);
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x12e17);
if (bVar1 == 0) {
  UnityEngine::ComponentExtensions::SafeSetActive(this->newMark,0);
}
else {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x12e17);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::ILFixDynamicMethodWrapper::Gen_Wrap_12(pIVar4,(undefined *)this,0);
}
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x12e18);
if (bVar1 != 0) {
  pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x12e18);
  if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  puStack_38 = (undefined *)0x0;
  pCVar17 = IFix::Core::Call::Begin();
  puStack_38 = pCVar17->topWriteBack;
  if (pIVar4->anonObj != (undefined *)0x0) {
    IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffffa8,pIVar4->anonObj);
  }
  IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffffa8,(undefined *)this);
  if ((VirtualMachine *)pIVar4->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  IFix::Core::VirtualMachine::Execute
            ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,
             (Call *)&stack0xffffffffffffffa8,(pIVar4->anonObj != (undefined *)0x0) + 1,0);
  return;
}
uVar12._0_1_ = this->isUp;
uVar12._1_1_ = this->pad_91[0];
uVar12._2_1_ = this->pad_91[1];
uVar12._3_1_ = this->pad_91[2];
uVar12._4_1_ = this->pad_91[3];
uVar12._5_1_ = this->pad_91[4];
uVar12._6_1_ = this->pad_91[5];
uVar12._7_1_ = this->pad_91[6];
puVar9 = (undefined *)FUN_183997ba0(uVar12,_DAT_189b51450,0,0);
if (*(longlong *)&this->levelID == 0) {
  iVar20 = 0;
}
else {
  iVar20 = *(int *)(*(longlong *)&this->levelID + 0x14);
}
o = *(undefined **)&this->isUp;
uStack_30 = 0x180edcb12;
bVar1 = IFix::WrappersManagerImpl::IsPatched(0x107b);
if (bVar1 == 0) {
  if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
    uStack_30 = 0x180edcb2f;
    il2cpp::codegen::runtime_class_init();
  }
  uStack_30 = 0x180edcb34;
  bVar1 = ExcelMeta::ConstValueDataReaderExtend::get_NewWantedShowGenerationGradeTag();
  if (bVar1 != 0) {
    if (*(int *)(_DAT_1899efda8 + 0xe8) == 0) {
      uStack_30 = 0x180edcb52;
      il2cpp::codegen::runtime_class_init();
    }
    uStack_30 = 0x180edcb59;
    this_00 = ExcelMeta::MPKOGHAEEFM::HBDPKMEMLFF(iVar20);
    if (this_00 == (MJOMKLJCHND *)0x0) {
      value = (undefined *)**(undefined8 **)(_DAT_1899de428 + 0x28);
    }
    else {
      uStack_30 = 0x180edcb76;
      value = ExcelMeta::MJOMKLJCHND::CMCNFBLOGPN(this_00);
    }
    uStack_30 = 0x180edcb81;
    bVar1 = System::String::IsNullOrEmpty(value);
    uStack_30 = 0x180edcb94;
    UnityEngine::ComponentExtensions::SafeSetActive(o,bVar1 == 0,0);
    if (bVar1 == 0) {
      uStack_30 = 0x180edcba6;
      UnityEngine::UI::TextExtensions::SafeSetText(puVar9,value,1);
    }
  }
  return;
}
uStack_30 = 0x180edcbc5;
pIVar4 = IFix::WrappersManagerImpl::GetPatch(0x107b);
if (pIVar4 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
  uStack_30 = 0x180edcbef;
  il2cpp::codegen::raise_null_reference_exception();
}
puStack_38 = (undefined *)0x0;
pCVar17 = IFix::Core::Call::Begin();
puStack_38 = pCVar17->topWriteBack;
if (pIVar4->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffffa8,pIVar4->anonObj);
}
IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffffa8,o);
IFix::Core::Call::PushObject((Call *)&stack0xffffffffffffffa8,puVar9);
IFix::Core::Call::PushInt32((Call *)&stack0xffffffffffffffa8,iVar20);
if ((VirtualMachine *)pIVar4->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar4->virtualMachine,pIVar4->methodId,
           (Call *)&stack0xffffffffffffffa8,(pIVar4->anonObj != (undefined *)0x0) + 3,0);
return;\