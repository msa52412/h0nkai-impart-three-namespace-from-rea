
DOCKBAEKMAN *pDVar1;
CFINMGJAHEA *pCVar2;
KOEHFENAMHN *pKVar3;
LPMACAAOBDA *pLVar4;
StigmataDataItem *pSVar5;
WeaponDataItem *pWVar6;
longlong lVar7;
bool bVar8;
byte bVar9;
uint uVar10;
KeyGeneratedEventHandler *this_00;
DOCKBAEKMAN *pDVar11;
RichTextSubHelper *this_01;
TextID TVar12;
longlong *plVar13;
longlong *plVar14;
CFINMGJAHEA *pCVar15;
undefined *puVar16;
undefined *puVar17;
longlong lVar18;
ILFixDynamicMethodWrapper *pIVar19;
Call *pCVar20;
undefined8 uVar21;
longlong *plVar22;
KOEHFENAMHN *furnitureData;
LPMACAAOBDA *mechDataItem;
StigmataDataItem *stigmata;
WeaponDataItem *weaponData;
WeaponDataItem *this_02;
Call CStack_58;
undefined8 uStack_30;

uStack_30 = 0x1827a16a3;
bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16244);
if (bVar9 == 0) {
  uStack_30 = 0x1827a16b8;
  SetupDefaultDisplay(this);
  plVar13 = *(longlong **)&this->needListenNotify;
  plVar22 = (longlong *)0x0;
  if (plVar13 != (longlong *)0x0) {
    if ((*(byte *)(*plVar13 + 0x132) < *(byte *)(_DAT_189a15a50 + 0x132)) ||
       (bVar8 = true,
       *(longlong *)
        (*(longlong *)(*plVar13 + 0x50) +
        (longlong)(int)(*(byte *)(_DAT_189a15a50 + 0x132) - 1) * 8) != _DAT_189a15a50)) {
      bVar8 = false;
    }
    plVar14 = plVar22;
    if (bVar8) {
      plVar14 = plVar13;
    }
    if (plVar14 != (longlong *)0x0) {
      CStack_58.currentTop = (undefined *)0x1827a25a3;
      bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16246);
      if (bVar9 == 0) {
        CStack_58.currentTop = (undefined *)0x1827a25be;
        UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelSize,1);
        pWVar6 = *(WeaponDataItem **)&this->needListenNotify;
        if ((MonoWeaponRenderImage *)this->t_3dModelRectTrans == (MonoWeaponRenderImage *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a2786;
          il2cpp::codegen::raise_null_reference_exception();
        }
        this_02 = (WeaponDataItem *)0x0;
        weaponData = this_02;
        if (pWVar6 != (WeaponDataItem *)0x0) {
          if (((byte)pWVar6->__klass[0x132] < *(byte *)(_DAT_189a15a50 + 0x132)) ||
             (bVar8 = true,
             *(longlong *)
              (*(longlong *)(pWVar6->__klass + 0x50) +
              (longlong)(int)(*(byte *)(_DAT_189a15a50 + 0x132) - 1) * 8) != _DAT_189a15a50)) {
            bVar8 = false;
          }
          weaponData = (WeaponDataItem *)0x0;
          if (bVar8) {
            weaponData = pWVar6;
          }
        }
        CStack_58.currentTop = (undefined *)0x1827a2637;
        MonoWeaponRenderImage::SetupView
                  ((MonoWeaponRenderImage *)this->t_3dModelRectTrans,weaponData,0,0,0);
        if ((LNFBAFMHDEH *)this->data == (LNFBAFMHDEH *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a2780;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1827a2658;
        LNFBAFMHDEH::LJJGJAPGFCG
                  ((LNFBAFMHDEH *)this->data,(MonoAnimationinSequence *)this->weaponRenderImage,
                   (undefined *)0x0);
        pWVar6 = *(WeaponDataItem **)&this->needListenNotify;
        if (pWVar6 != (WeaponDataItem *)0x0) {
          if (((byte)pWVar6->__klass[0x132] < *(byte *)(_DAT_189a15a50 + 0x132)) ||
             (bVar8 = true,
             *(longlong *)
              (*(longlong *)(pWVar6->__klass + 0x50) +
              (longlong)(int)(*(byte *)(_DAT_189a15a50 + 0x132) - 1) * 8) != _DAT_189a15a50)) {
            bVar8 = false;
          }
          if (bVar8) {
            this_02 = pWVar6;
          }
        }
        CStack_58.currentTop = (undefined *)0x1827a26aa;
        UnityEngine::ComponentExtensions::SafeSetActive(this->titleText,1);
        puVar17 = this->titleText;
        CStack_58.currentTop = (undefined *)0x1827a26bd;
        lVar18 = FUN_183fba070(_DAT_189a9ad90);
        if (lVar18 == 0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a277a;
          il2cpp::codegen::raise_null_reference_exception();
        }
        lVar18 = *(longlong *)(lVar18 + 0x18);
        if (this_02 == (WeaponDataItem *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a2774;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.currentTop = (undefined *)0x1827a26eb;
        uVar10 = (**(code **)(this_02->__klass + 0x3b8))
                           (this_02,*(undefined8 *)(this_02->__klass + 0x3c0));
        if (lVar18 == 0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a276e;
          il2cpp::codegen::raise_null_reference_exception();
        }
        if (*(uint *)(lVar18 + 0x18) <= uVar10) {
          CStack_58.currentTop = (undefined *)0x1827a26fd;
          System::ThrowHelper::ThrowArgumentOutOfRangeException();
        }
        CStack_58.currentTop = (undefined *)0x1827a2711;
        UnityEngine::UI::ImageExtensions::SafeSetSprite
                  (puVar17,*(undefined8 *)
                            (*(longlong *)(lVar18 + 0x10) + 0x20 + (longlong)(int)uVar10 * 8),1);
        CStack_58.currentTop = (undefined *)0x1827a2719;
        bVar9 = WeaponDataItem::get_IsExWeapon(this_02);
        if (bVar9 != 0) {
          CStack_58.currentTop = (undefined *)0x1827a2730;
          UnityEngine::ComponentExtensions::SafeSetActive(this->otherIconAnimSequence,1);
        }
        return;
      }
      CStack_58.currentTop = (undefined *)0x1827a2754;
      pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16246);
      if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1827a278c;
        il2cpp::codegen::raise_null_reference_exception();
      }
      goto IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13;
    }
  }
  if (plVar13 != (longlong *)0x0) {
    if ((*(byte *)(*plVar13 + 0x132) < *(byte *)(_DAT_189a17b80 + 0x132)) ||
       (plVar14 = (longlong *)0x1,
       *(longlong *)
        (*(longlong *)(*plVar13 + 0x50) +
        (longlong)(int)(*(byte *)(_DAT_189a17b80 + 0x132) - 1) * 8) != _DAT_189a17b80)) {
      plVar14 = plVar22;
    }
    if ((char)plVar14 != '\0') {
      plVar22 = plVar13;
    }
    if (plVar22 != (longlong *)0x0) {
      CStack_58.currentTop = (undefined *)0x1827a1a73;
      bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16247);
      if (bVar9 != 0) {
        CStack_58.currentTop = (undefined *)0x1827a1b25;
        pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16247);
        if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
          CStack_58.currentTop = (undefined *)0x1827a1b4b;
          il2cpp::codegen::raise_null_reference_exception();
        }
        goto IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13;
      }
      CStack_58.currentTop = (undefined *)0x1827a1a8e;
      UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelSize,1);
      pKVar3 = *(KOEHFENAMHN **)&this->needListenNotify;
      if ((MonoWeaponRenderImage *)this->t_3dModelRectTrans == (MonoWeaponRenderImage *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1827a1b45;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (pKVar3 == (KOEHFENAMHN *)0x0) {
        furnitureData = (KOEHFENAMHN *)0x0;
      }
      else {
        if (((byte)pKVar3->__klass[0x132] < *(byte *)(_DAT_189a17b80 + 0x132)) ||
           (*(longlong *)
             (*(longlong *)(pKVar3->__klass + 0x50) +
             (longlong)(int)(*(byte *)(_DAT_189a17b80 + 0x132) - 1) * 8) != _DAT_189a17b80)) {
          bVar8 = false;
        }
        else {
          bVar8 = true;
        }
        furnitureData = (KOEHFENAMHN *)0x0;
        if (bVar8) {
          furnitureData = pKVar3;
        }
      }
      CStack_58.currentTop = (undefined *)0x1827a1afe;
      MonoWeaponRenderImage::SetupView
                ((MonoWeaponRenderImage *)this->t_3dModelRectTrans,furnitureData,0,0,0);
      puVar17 = this->data;
      if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1827a1b3f;
        il2cpp::codegen::raise_null_reference_exception();
      }
      plVar13 = (longlong *)this->weaponRenderImage;
      goto code_r0x000181fa1600;
    }
  }
  uStack_30 = 0x1827a177b;
  lVar18 = func_0x000180257760(plVar13,_DAT_189a1ad48);
  if (lVar18 == 0) {
    uStack_30 = 0x1827a1793;
    lVar18 = func_0x000180257760(plVar13,_DAT_189a15a58);
    if (lVar18 == 0) {
      uStack_30 = 0x1827a17ab;
      lVar18 = func_0x000180257760(plVar13,_DAT_189a15818);
      if (lVar18 == 0) {
        uStack_30 = 0x1827a17bf;
        lVar18 = func_0x000180257760(plVar13,_DAT_189a18310);
        if (lVar18 == 0) {
          uStack_30 = 0x1827a17d3;
          lVar18 = func_0x000180257760(plVar13);
          if (lVar18 == 0) {
            uStack_30 = 0x1827a1e03;
            bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16251);
            if (bVar9 == 0) {
              uStack_30 = 0x1827a1e23;
              UnityEngine::ComponentExtensions::SafeSetActive(this->elfStarImg,1);
              plVar13 = *(longlong **)&this->needListenNotify;
              puVar17 = this->otherIconTrans;
              if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
                uStack_30 = 0x1827a1ecb;
                il2cpp::codegen::raise_null_reference_exception();
              }
              uStack_30 = 0x1827a1e47;
              uVar21 = (**(code **)(*plVar13 + 0x208))(plVar13,*(undefined8 *)(*plVar13 + 0x210));
              uStack_30 = 0x1827a1e55;
              UnityEngine::UI::ImageExtensions::SafeSetSprite(puVar17,uVar21);
              if ((LNFBAFMHDEH *)this->data == (LNFBAFMHDEH *)0x0) {
                  /* WARNING: Subroutine does not return */
                uStack_30 = 0x1827a1ec5;
                il2cpp::codegen::raise_null_reference_exception();
              }
              uStack_30 = 0x1827a1e6d;
              LNFBAFMHDEH::LJJGJAPGFCG
                        ((LNFBAFMHDEH *)this->data,(MonoAnimationinSequence *)this->otherIconImg,
                         (undefined *)0x0);
              plVar13 = *(longlong **)&this->needListenNotify;
              if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
                uStack_30 = 0x1827a1ebf;
                il2cpp::codegen::raise_null_reference_exception();
              }
              uStack_30 = 0x1827a1e86;
              puVar17 = (undefined *)
                        (**(code **)(*plVar13 + 0x318))(plVar13,*(undefined8 *)(*plVar13 + 800));
              uStack_30 = 0x1827a151a;
              bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16252);
              if (bVar9 != 0) {
                uStack_30 = 0x1827a1638;
                pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16252);
                if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
                  uStack_30 = 0x1827a1680;
                  il2cpp::codegen::raise_null_reference_exception();
                }
                CStack_58.argumentBase = (undefined *)0x0;
                CStack_58.evaluationStackBase = (undefined *)0x0;
                CStack_58.managedStack = (undefined *)0x0;
                CStack_58.currentTop = (undefined *)0x0;
                CStack_58.topWriteBack = (undefined *)0x0;
                pCVar20 = IFix::Core::Call::Begin();
                CStack_58.argumentBase = pCVar20->argumentBase;
                CStack_58.evaluationStackBase = pCVar20->evaluationStackBase;
                CStack_58.managedStack = pCVar20->managedStack;
                CStack_58.currentTop = pCVar20->currentTop;
                CStack_58.topWriteBack = pCVar20->topWriteBack;
                if (pIVar19->anonObj != (undefined *)0x0) {
                  IFix::Core::Call::PushObject(&CStack_58,pIVar19->anonObj);
                }
                IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
                IFix::Core::Call::PushObject(&CStack_58,puVar17);
                if ((VirtualMachine *)pIVar19->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
                  il2cpp::codegen::raise_null_reference_exception();
                }
                IFix::Core::VirtualMachine::Execute
                          ((VirtualMachine *)pIVar19->virtualMachine,pIVar19->methodId,&CStack_58,
                           (pIVar19->anonObj != (undefined *)0x0) + 2,0);
                return;
              }
              uStack_30 = 0x1827a152a;
              bVar9 = System::String::IsNullOrEmpty(puVar17);
              if (bVar9 == 0) {
                uStack_30 = 0x1827a1554;
                UnityEngine::ComponentExtensions::SafeSetActive(this->titleAnimSequence,1);
                uStack_30 = 0x1827a1560;
                this_01 = (RichTextSubHelper *)il2cpp::codegen::object_new(_DAT_189a1ad50);
                uStack_30 = 0x1827a156e;
                PlotTrackLine::RichTextSubHelper::_ctor(this_01,puVar17);
                uStack_30 = 0x1827a1579;
                bVar9 = NeedSubString(this,this_01);
                if (bVar9 != 0) {
                  if (*(int *)(_DAT_1899e7158 + 0xe8) == 0) {
                    uStack_30 = 0x1827a1596;
                    il2cpp::codegen::runtime_class_init();
                  }
                  uStack_30 = 0x1827a15a2;
                  TVar12 = TextID::op_Implicit(_DAT_189b79220);
                  uStack_30 = 0x1827a15b5;
                  plVar13 = (longlong *)func_0x0001804fe0c0(_DAT_1899de3d0,1);
                  uStack_30 = 0x1827a15c6;
                  puVar17 = Substring(this,this_01,puVar17);
                  if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
                    uStack_30 = 0x1827a167a;
                    il2cpp::codegen::raise_null_reference_exception();
                  }
                  if (puVar17 != (undefined *)0x0) {
                    uStack_30 = 0x1827a15e6;
                    lVar18 = thunk_FUN_180442320(puVar17,*(undefined8 *)(*plVar13 + 0x30));
                    if (lVar18 == 0) {
                      uStack_30 = 0x1827a165a;
                      uVar21 = il2cpp::codegen::get_array_type_mismatch_exception();
                  /* WARNING: Subroutine does not return */
                      uStack_30 = 0x1827a1664;
                      il2cpp::codegen::raise_exception(uVar21,0);
                    }
                  }
                  if ((int)plVar13[3] == 0) {
                    uStack_30 = 0x1827a166a;
                    uVar21 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
                    uStack_30 = 0x1827a1674;
                    il2cpp::codegen::raise_exception(uVar21,0);
                  }
                  plVar13[4] = (longlong)puVar17;
                  uStack_30 = 0x1827a15ff;
                  puVar17 = LocalizationGeneralLogic::GetText
                                      ((TextID)((ulonglong)TVar12 & 0xffffffff),
                                       (undefined *)plVar13);
                }
                uStack_30 = 0x1827a1614;
                UnityEngine::UI::TextExtensions::SafeSetText(this->detailTrans,puVar17,1);
              }
              return;
            }
            uStack_30 = 0x1827a1ea5;
            pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16251);
            if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
              uStack_30 = 0x1827a1ed1;
              il2cpp::codegen::raise_null_reference_exception();
            }
          }
          else {
            uStack_30 = 0x1827a12a3;
            bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16250);
            if (bVar9 == 0) {
              pDVar1 = *(DOCKBAEKMAN **)&this->needListenNotify;
              if (pDVar1 != (DOCKBAEKMAN *)0x0) {
                puVar17 = pDVar1->__klass;
                if (((byte)puVar17[0x132] < *(byte *)(_DAT_189a17428 + 0x132)) ||
                   (bVar8 = true,
                   *(longlong *)
                    (*(longlong *)(puVar17 + 0x50) +
                    (longlong)(int)(*(byte *)(_DAT_189a17428 + 0x132) - 1) * 8) != _DAT_189a17428)
                   ) {
                  bVar8 = false;
                }
                pDVar11 = (DOCKBAEKMAN *)0x0;
                if (bVar8) {
                  pDVar11 = pDVar1;
                }
                if (pDVar11 != (DOCKBAEKMAN *)0x0) {
                  if (((byte)puVar17[0x132] < *(byte *)(_DAT_189a17428 + 0x132)) ||
                     (bVar8 = true,
                     *(longlong *)
                      (*(longlong *)(puVar17 + 0x50) +
                      (longlong)(int)(*(byte *)(_DAT_189a17428 + 0x132) - 1) * 8) !=
                     _DAT_189a17428)) {
                    bVar8 = false;
                  }
                  pDVar11 = (DOCKBAEKMAN *)0x0;
                  if (bVar8) {
                    pDVar11 = pDVar1;
                  }
                  uStack_30 = 0x1827a133c;
                  puVar17 = DOCKBAEKMAN::KHLBGJJPKOL(pDVar11);
                  uStack_30 = 0x1827a1352;
                  UnityEngine::ComponentExtensions::SafeSetActive(this->elfStarImg,1);
                  uStack_30 = 0x1827a1364;
                  UnityEngine::UI::ImageExtensions::SafeSetSprite(this->otherIconTrans,puVar17);
                  puVar17 = this->data;
                  if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
                    uStack_30 = 0x1827a13aa;
                    il2cpp::codegen::raise_null_reference_exception();
                  }
                  plVar13 = (longlong *)this->otherIconImg;
                  goto code_r0x000181fa1600;
                }
              }
                  /* WARNING: Subroutine does not return */
              uStack_30 = 0x1827a13b0;
              il2cpp::codegen::raise_null_reference_exception();
            }
            uStack_30 = 0x1827a1390;
            pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16250);
            if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
              uStack_30 = 0x1827a13b6;
              il2cpp::codegen::raise_null_reference_exception();
            }
          }
        }
        else {
          uStack_30 = 0x1827a1903;
          bVar9 = IFix::WrappersManagerImpl::IsPatched(0x1624f);
          if (bVar9 == 0) {
            uStack_30 = 0x1827a1923;
            UnityEngine::ComponentExtensions::SafeSetActive(this->avatarCardAnimSequence);
            pCVar2 = *(CFINMGJAHEA **)&this->needListenNotify;
            puVar17 = this->elfStarsTrans;
            if (pCVar2 != (CFINMGJAHEA *)0x0) {
              puVar16 = pCVar2->__klass;
              if (((byte)puVar16[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
                 (bVar8 = true,
                 *(longlong *)
                  (*(longlong *)(puVar16 + 0x50) +
                  (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8) != _DAT_189a18310))
              {
                bVar8 = false;
              }
              pCVar15 = (CFINMGJAHEA *)0x0;
              if (bVar8) {
                pCVar15 = pCVar2;
              }
              if (pCVar15 != (CFINMGJAHEA *)0x0) {
                if (((byte)puVar16[0x132] < *(byte *)(_DAT_189a18310 + 0x132)) ||
                   (bVar8 = true,
                   *(longlong *)
                    (*(longlong *)(puVar16 + 0x50) +
                    (longlong)(int)(*(byte *)(_DAT_189a18310 + 0x132) - 1) * 8) != _DAT_189a18310)
                   ) {
                  bVar8 = false;
                }
                pCVar15 = (CFINMGJAHEA *)0x0;
                if (bVar8) {
                  pCVar15 = pCVar2;
                }
                uStack_30 = 0x1827a19b6;
                puVar16 = CFINMGJAHEA::NKJPAJHFGFC(pCVar15);
                uStack_30 = 0x1827a19c4;
                UnityEngine::UI::ImageExtensions::SafeSetSprite(puVar17,puVar16,1);
                uStack_30 = 0x1827a19d7;
                UnityEngine::ComponentExtensions::SafeSetActive(this->elfStarImg,1);
                plVar13 = *(longlong **)&this->needListenNotify;
                puVar17 = this->otherIconTrans;
                if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
                  uStack_30 = 0x1827a1a51;
                  il2cpp::codegen::raise_null_reference_exception();
                }
                uStack_30 = 0x1827a19f7;
                uVar21 = (**(code **)(*plVar13 + 0x208))
                                   (plVar13,*(undefined8 *)(*plVar13 + 0x210));
                uStack_30 = 0x1827a1a05;
                UnityEngine::UI::ImageExtensions::SafeSetSprite(puVar17,uVar21);
                puVar17 = this->data;
                if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
                  uStack_30 = 0x1827a1a4b;
                  il2cpp::codegen::raise_null_reference_exception();
                }
                plVar13 = (longlong *)this->otherIconImg;
                goto code_r0x000181fa1600;
              }
            }
                  /* WARNING: Subroutine does not return */
            uStack_30 = 0x1827a1a57;
            il2cpp::codegen::raise_null_reference_exception();
          }
          uStack_30 = 0x1827a1a31;
          pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x1624f);
          if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
            uStack_30 = 0x1827a1a5d;
            il2cpp::codegen::raise_null_reference_exception();
          }
        }
      }
      else {
        uStack_30 = 0x1827a11f3;
        bVar9 = IFix::WrappersManagerImpl::IsPatched(0x1624e);
        if (bVar9 == 0) {
          uStack_30 = 0x1827a120f;
          UnityEngine::ComponentExtensions::SafeSetActive(this->stigmataAnimSequence,1);
          plVar13 = *(longlong **)&this->needListenNotify;
          puVar17 = this->avatarCardTrans;
          if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
            uStack_30 = 0x1827a1289;
            il2cpp::codegen::raise_null_reference_exception();
          }
          uStack_30 = 0x1827a122f;
          uVar21 = (**(code **)(*plVar13 + 0x208))(plVar13,*(undefined8 *)(*plVar13 + 0x210));
          uStack_30 = 0x1827a123d;
          UnityEngine::UI::ImageExtensions::SafeSetSprite(puVar17,uVar21);
          puVar17 = this->data;
          if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
            uStack_30 = 0x1827a1283;
            il2cpp::codegen::raise_null_reference_exception();
          }
          plVar13 = (longlong *)this->avatarCardImg;
          goto code_r0x000181fa1600;
        }
        uStack_30 = 0x1827a1269;
        pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x1624e);
        if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
          uStack_30 = 0x1827a128f;
          il2cpp::codegen::raise_null_reference_exception();
        }
      }
    }
    else {
      uStack_30 = 0x1827a2303;
      bVar9 = IFix::WrappersManagerImpl::IsPatched(0x1624b);
      if (bVar9 == 0) {
        uStack_30 = 0x1827a231e;
        UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelAnimSequence);
        pSVar5 = *(StigmataDataItem **)&this->needListenNotify;
        if ((MonoStigmataFigure *)this->stigmataIconTrans == (MonoStigmataFigure *)0x0) {
                  /* WARNING: Subroutine does not return */
          uStack_30 = 0x1827a23c0;
          il2cpp::codegen::raise_null_reference_exception();
        }
        stigmata = (StigmataDataItem *)0x0;
        if (pSVar5 != (StigmataDataItem *)0x0) {
          if (((byte)pSVar5->__klass[0x132] < *(byte *)(_DAT_189a15a58 + 0x132)) ||
             (bVar8 = true,
             *(longlong *)
              (*(longlong *)(pSVar5->__klass + 0x50) +
              (longlong)(int)(*(byte *)(_DAT_189a15a58 + 0x132) - 1) * 8) != _DAT_189a15a58)) {
            bVar8 = false;
          }
          if (bVar8) {
            stigmata = pSVar5;
          }
        }
        uStack_30 = 0x1827a2379;
        MonoStigmataFigure::SetupView((MonoStigmataFigure *)this->stigmataIconTrans,stigmata);
        puVar17 = this->data;
        if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
          uStack_30 = 0x1827a23ba;
          il2cpp::codegen::raise_null_reference_exception();
        }
        plVar13 = (longlong *)this->stigmataFigure;
        goto code_r0x000181fa1600;
      }
      uStack_30 = 0x1827a23a0;
      pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x1624b);
      if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x1827a23c6;
        il2cpp::codegen::raise_null_reference_exception();
      }
    }
  }
  else {
    CStack_58.currentTop = (undefined *)0x1827a1bd3;
    bVar9 = IFix::WrappersManagerImpl::IsPatched(0x16249);
    if (bVar9 == 0) {
      CStack_58.currentTop = (undefined *)0x1827a1bee;
      UnityEngine::ComponentExtensions::SafeSetActive(this->t_3dModelSize,1);
      pLVar4 = *(LPMACAAOBDA **)&this->needListenNotify;
      if ((MonoWeaponRenderImage *)this->t_3dModelRectTrans == (MonoWeaponRenderImage *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1827a1ca5;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (pLVar4 == (LPMACAAOBDA *)0x0) {
        mechDataItem = (LPMACAAOBDA *)0x0;
      }
      else {
        if (((byte)pLVar4->__klass[0x132] < *(byte *)(_DAT_189a1ad48 + 0x132)) ||
           (*(longlong *)
             (*(longlong *)(pLVar4->__klass + 0x50) +
             (longlong)(int)(*(byte *)(_DAT_189a1ad48 + 0x132) - 1) * 8) != _DAT_189a1ad48)) {
          bVar8 = false;
        }
        else {
          bVar8 = true;
        }
        mechDataItem = (LPMACAAOBDA *)0x0;
        if (bVar8) {
          mechDataItem = pLVar4;
        }
      }
      CStack_58.currentTop = (undefined *)0x1827a1c5e;
      MonoWeaponRenderImage::SetupView
                ((MonoWeaponRenderImage *)this->t_3dModelRectTrans,mechDataItem,0,0,0);
      puVar17 = this->data;
      if (puVar17 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        CStack_58.currentTop = (undefined *)0x1827a1c9f;
        il2cpp::codegen::raise_null_reference_exception();
      }
      plVar13 = (longlong *)this->weaponRenderImage;
code_r0x000181fa1600:
      uStack_30 = 0x181fa1622;
      bVar9 = IFix::WrappersManagerImpl::IsPatched(0xc5f);
      if (bVar9 != 0) {
        uStack_30 = 0x181fa16bc;
        pIVar19 = IFix::WrappersManagerImpl::GetPatch(0xc5f);
        if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
          uStack_30 = 0x181fa16f2;
          il2cpp::codegen::raise_null_reference_exception();
        }
        CStack_58.argumentBase = (undefined *)0x0;
        CStack_58.evaluationStackBase = (undefined *)0x0;
        CStack_58.managedStack = (undefined *)0x0;
        CStack_58.currentTop = (undefined *)0x0;
        CStack_58.topWriteBack = (undefined *)0x0;
        pCVar20 = IFix::Core::Call::Begin();
        CStack_58.argumentBase = pCVar20->argumentBase;
        CStack_58.evaluationStackBase = pCVar20->evaluationStackBase;
        CStack_58.managedStack = pCVar20->managedStack;
        CStack_58.currentTop = pCVar20->currentTop;
        CStack_58.topWriteBack = pCVar20->topWriteBack;
        if (pIVar19->anonObj != (undefined *)0x0) {
          IFix::Core::Call::PushObject(&CStack_58,pIVar19->anonObj);
        }
        IFix::Core::Call::PushObject(&CStack_58,puVar17);
        IFix::Core::Call::PushObject(&CStack_58,(undefined *)plVar13);
        IFix::Core::Call::PushObject(&CStack_58,(undefined *)0x0);
        if ((VirtualMachine *)pIVar19->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
          il2cpp::codegen::raise_null_reference_exception();
        }
        IFix::Core::VirtualMachine::Execute
                  ((VirtualMachine *)pIVar19->virtualMachine,pIVar19->methodId,&CStack_58,
                   (pIVar19->anonObj != (undefined *)0x0) + 3,0);
        return;
      }
      uStack_30 = 0x181fa163b;
      this_00 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a2cc98);
      uStack_30 = 0x181fa1650;
      KeyGeneratedEventHandler::_ctor(this_00,puVar17,_DAT_189ac86f8);
      if (plVar13 == (longlong *)0x0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x181fa16ec;
        il2cpp::codegen::raise_null_reference_exception();
      }
      uStack_30 = 0x181fa1673;
      (**(code **)(*plVar13 + 0x188))(plVar13,this_00,0,*(undefined8 *)(*plVar13 + 400));
      uStack_30 = 0x181fa1686;
      (**(code **)(*plVar13 + 0x1a8))(plVar13,*(undefined8 *)(*plVar13 + 0x1b0));
      lVar18 = *(longlong *)(puVar17 + 0x10);
      if (lVar18 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x181fa16e6;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(longlong *)(lVar18 + 0x10) == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184c69ccc;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(int *)(lVar18 + 0x18) == *(int *)(*(longlong *)(lVar18 + 0x10) + 0x18)) {
        uStack_30 = 0x184c69c86;
        FUN_184883290(lVar18,*(int *)(lVar18 + 0x18) + 1,
                      *(undefined8 *)(*(longlong *)(*_DAT_189ac8700 + 0x90) + 0x58));
      }
      uVar10 = *(uint *)(lVar18 + 0x18);
      lVar7 = *(longlong *)(lVar18 + 0x10);
      *(uint *)(lVar18 + 0x18) = uVar10 + 1;
      if (lVar7 == 0) {
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184c69cc6;
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(uint *)(lVar7 + 0x18) <= uVar10) {
        uStack_30 = 0x184c69cb6;
        uVar21 = il2cpp::codegen::get_index_out_of_range_exception();
                  /* WARNING: Subroutine does not return */
        uStack_30 = 0x184c69cc0;
        il2cpp::codegen::raise_exception(uVar21,0);
      }
      *(longlong **)(lVar7 + 0x20 + (longlong)(int)uVar10 * 8) = plVar13;
      *(int *)(lVar18 + 0x1c) = *(int *)(lVar18 + 0x1c) + 1;
      return;
    }
    CStack_58.currentTop = (undefined *)0x1827a1c85;
    pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16249);
    if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
      CStack_58.currentTop = (undefined *)0x1827a1cab;
      il2cpp::codegen::raise_null_reference_exception();
    }
  }
}
else {
  uStack_30 = 0x1827a184b;
  pIVar19 = IFix::WrappersManagerImpl::GetPatch(0x16244);
  if (pIVar19 == (ILFixDynamicMethodWrapper *)0x0) {
                  /* WARNING: Subroutine does not return */
    uStack_30 = 0x1827a1865;
    il2cpp::codegen::raise_null_reference_exception();
  }
}
IFix_ILFixDynamicMethodWrapper_Gen_Wrap_13:
CStack_58.argumentBase = (undefined *)0x0;
CStack_58.evaluationStackBase = (undefined *)0x0;
CStack_58.managedStack = (undefined *)0x0;
CStack_58.currentTop = (undefined *)0x0;
CStack_58.topWriteBack = (undefined *)0x0;
pCVar20 = IFix::Core::Call::Begin();
CStack_58.argumentBase = pCVar20->argumentBase;
CStack_58.evaluationStackBase = pCVar20->evaluationStackBase;
CStack_58.managedStack = pCVar20->managedStack;
CStack_58.currentTop = pCVar20->currentTop;
CStack_58.topWriteBack = pCVar20->topWriteBack;
if (pIVar19->anonObj != (undefined *)0x0) {
  IFix::Core::Call::PushObject(&CStack_58,pIVar19->anonObj);
}
IFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
if ((VirtualMachine *)pIVar19->virtualMachine == (VirtualMachine *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
IFix::Core::VirtualMachine::Execute
          ((VirtualMachine *)pIVar19->virtualMachine,pIVar19->methodId,&CStack_58,
           (pIVar19->anonObj != (undefined *)0x0) + 1,0);
return;\