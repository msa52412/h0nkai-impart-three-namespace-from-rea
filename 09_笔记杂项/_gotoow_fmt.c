\nint iVar1;
\nlonglong lVar2;
\nTwoEndless *this_00;
\nundefined *puVar3;
\nbyte bVar4;
\nchar cVar5;
\nushort CFLNPMMIHLB;
\nuint uVar6;
\nLoadingWheelWidgetForTwoRspContext *this_01;
\nKeyGeneratedEventHandler *this_02;
\nException *this_03;
\nILFixDynamicMethodWrapper *pIVar7;
\nType *type;
\nDateTime *pDVar8;
\nJAHPKOOJOGP *this_04;
\nCall *pCVar9;
\nbool bVar10;
\nCall CStack_58;
\nundefined8 uStack_30;
\n\nuStack_30 = 0x1819c5e13;
\nbVar4 = IFix::WrappersManagerImpl::IsPatched(0x108d7);
\nif (bVar4 == 0) {
\n  uStack_30 = 0x1819c5e2c;
\n  this_01 = (LoadingWheelWidgetForTwoRspContext *)il2cpp::codegen::object_new(_DAT_189a19890);
\n  uStack_30 = 0x1819c5e43;
\n  LoadingWheelWidgetForTwoRspContext::_ctor(this_01,0xd5c,0xd7c,(Action *)0x0);
\n  if (this_01 == (LoadingWheelWidgetForTwoRspContext *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n    uStack_30 = 0x1819c5f60;
\n    il2cpp::codegen::raise_null_reference_exception();
\n  }
\n  uStack_30 = 0x1819c5e5e;
\n  LoadingWheelWidgetForTwoRspContext::SetIgnoreMaxWaitTimeForReq(this_01,0xd5b);
\n  uStack_30 = 0x1819c5e6a;
\n  this_02 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_189a15430);
\n  uStack_30 = 0x1819c5e82;
\n  KeyGeneratedEventHandler::_ctor(this_02,(undefined *)this,_DAT_189b0e4b8);
\n  this_01->cmdCallBack = (undefined *)this_02;
\n  lVar2 = *_DAT_189a985c0;
\n  if (*(char *)(lVar2 + 0x136) == '\0') {
\n    uStack_30 = 0x1819c5ea4;
\n    FUN_18043e4c0(lVar2);
\n  }
\n  lVar2 = **(longlong **)(lVar2 + 0x90);
\n  if (*(char *)(lVar2 + 0x136) == '\0') {
\n    uStack_30 = 0x1819c5ebf;
\n    FUN_18043e4c0(lVar2);
\n  }
\n  if ((MainUIManager *)**(undefined8 **)(lVar2 + 0x28) == (MainUIManager *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n    uStack_30 = 0x1819c5f5a;
\n    il2cpp::codegen::raise_null_reference_exception();
\n  }
\n  uStack_30 = 0x1819c5eda;
\n  MainUIManager::ShowWidget\n            ((MainUIManager *)**(undefined8 **)(lVar2 + 0x28),(BaseWidgetContext *)this_01,0);
\n  lVar2 = *_DAT_189a981a8;
\n  if (*(char *)(lVar2 + 0x136) == '\0') {
\n    uStack_30 = 0x1819c5ef5;
\n    FUN_18043e4c0(lVar2);
\n  }
\n  lVar2 = **(longlong **)(lVar2 + 0x90);
\n  if (*(char *)(lVar2 + 0x136) == '\0') {
\n    uStack_30 = 0x1819c5f10;
\n    FUN_18043e4c0(lVar2);
\n  }
\n  this = (OWEndlessModule *)**(undefined8 **)(lVar2 + 0x28);
\n  if ((NetworkManager *)this == (NetworkManager *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n    uStack_30 = 0x1819c5f54;
\n    il2cpp::codegen::raise_null_reference_exception();
\n  }
\n  uStack_30 = 0x181ac59e3;
\n  bVar4 = IFix::WrappersManagerImpl::IsPatched(0x2865);
\n  if (bVar4 == 0) {
\n    lVar2 = *_DAT_189a9c530;
\n    if (*(char *)(lVar2 + 0x136) == '\0') {
\n      uStack_30 = 0x181ac5a0b;
\n      FUN_18043e4c0(lVar2);
\n    }
\n    lVar2 = **(longlong **)(lVar2 + 0x90);
\n    if (*(char *)(lVar2 + 0x136) == '\0') {
\n      uStack_30 = 0x181ac5a26;
\n      FUN_18043e4c0(lVar2);
\n    }
\n    if (**(longlong **)(lVar2 + 0x28) == 0) {
\n                  /* WARNING: Subroutine does not return */\n      uStack_30 = 0x181ac5b10;
\n      il2cpp::codegen::raise_null_reference_exception();
\n    }
\n    this_00 = *(TwoEndless **)(**(longlong **)(lVar2 + 0x28) + 0x58);
\n    if (this_00 == (TwoEndless *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n      uStack_30 = 0x181ac5b0a;
\n      il2cpp::codegen::raise_null_reference_exception();
\n    }
\n    uStack_30 = 0x181ac5a4d;
\n    uVar6 = TwoEndless::GetActiveMode(this_00);
\n    lVar2 = *_DAT_189a9c530;
\n    if (*(char *)(lVar2 + 0x136) == '\0') {
\n      uStack_30 = 0x181ac5a6a;
\n      FUN_18043e4c0(lVar2);
\n    }
\n    lVar2 = **(longlong **)(lVar2 + 0x90);
\n    if (*(char *)(lVar2 + 0x136) == '\0') {
\n      uStack_30 = 0x181ac5a85;
\n      FUN_18043e4c0(lVar2);
\n    }
\n    if ((OWEndlessModule *)**(undefined8 **)(lVar2 + 0x28) == (OWEndlessModule *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n      uStack_30 = 0x181ac5b04;
\n      il2cpp::codegen::raise_null_reference_exception();
\n    }
\n    bVar4 = (byte)uVar6;
\n    uStack_30 = 0x181ac5a98;
\n    uVar6 = ModeToType((OWEndlessModule *)**(undefined8 **)(lVar2 + 0x28),uVar6);
\n    uStack_30 = 0x181ac5aa6;
\n    this_03 = (Exception *)il2cpp::codegen::object_new(_DAT_189a057a8);
\n    uStack_30 = 0x181ac5ab1;
\n    UnityEngine::WWWTranscoder::ByteArrayContains((undefined *)this_03,bVar4);
\n    if (this_03 == (Exception *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n      uStack_30 = 0x181ac5afe;
\n      il2cpp::codegen::raise_null_reference_exception();
\n    }
\n    *(uint *)((longlong)&this_03->s_EDILock + 4) = uVar6;
\n    if (*(int *)(_DAT_1899e6f70 + 0xe8) == 0) {
\n      uStack_30 = 0x1837201c8;
\n      il2cpp::codegen::runtime_class_init(_DAT_1899e6f70,this_03,_DAT_189aa7058);
\n    }
\n    if (*(char *)(*(longlong *)(_DAT_1899e6f70 + 0x28) + 1) == '\0') {
\n      if (this_03 == (Exception *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n        uStack_30 = 0x18372042c;
\n        il2cpp::codegen::raise_null_reference_exception();
\n      }
\n      uStack_30 = 0x1837201f8;
\n      type = (Type *)System::Object::GetType(this_03);
\n      if (*(int *)(_DAT_189a1cd78 + 0xe8) == 0) {
\n        uStack_30 = 0x183720210;
\n        il2cpp::codegen::runtime_class_init();
\n      }
\n      uStack_30 = 0x183720218;
\n      CFLNPMMIHLB = CommandMap::GetCmdIDByType(type);
\n      if ((NetworkManager *)this == (NetworkManager *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n        uStack_30 = 0x183720426;
\n        il2cpp::codegen::raise_null_reference_exception();
\n      }
\n      uStack_30 = 0x183720237;
\n      bVar4 = NetworkManager::CheckRequestTimeValid((NetworkManager *)this,(uint)CFLNPMMIHLB);
\n      if (bVar4 != 0) {
\n        puVar3 = ((NetworkManager *)this)->syncTimeManager;
\n        if (*(int *)(_DAT_189a15420 + 0xe8) == 0) {
\n          uStack_30 = 0x183720258;
\n          il2cpp::codegen::runtime_class_init();
\n        }
\n        uStack_30 = 0x18372025d;
\n        pDVar8 = TimeUtil::get_NowDateTime();
\n        if (puVar3 == (undefined *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n          uStack_30 = 0x183720420;
\n          il2cpp::codegen::raise_null_reference_exception();
\n        }
\n        uStack_30 = 0x183720276;
\n        FUN_184e77c10(puVar3,CFLNPMMIHLB,pDVar8,0);
\n        uStack_30 = 0x183720282;
\n        this_04 = (JAHPKOOJOGP *)il2cpp::codegen::object_new(_DAT_189a1cd08);
\n        uStack_30 = 0x18372028d;
\n        JAHPKOOJOGP::_ctor(this_04);
\n        lVar2 = *_DAT_189a98668;
\n        if (*(char *)(lVar2 + 0x136) == '\0') {
\n          uStack_30 = 0x1837202a8;
\n          FUN_18043e4c0(lVar2);
\n        }
\n        lVar2 = **(longlong **)(lVar2 + 0x90);
\n        if (*(char *)(lVar2 + 0x136) == '\0') {
\n          uStack_30 = 0x1837202c3;
\n          FUN_18043e4c0(lVar2);
\n        }
\n        if (**(longlong **)(lVar2 + 0x28) == 0) {
\n                  /* WARNING: Subroutine does not return */\n          uStack_30 = 0x18372041a;
\n          il2cpp::codegen::raise_null_reference_exception();
\n        }
\n        lVar2 = *(longlong *)(**(longlong **)(lVar2 + 0x28) + 0x48);
\n        if (lVar2 == 0) {
\n                  /* WARNING: Subroutine does not return */\n          uStack_30 = 0x183720414;
\n          il2cpp::codegen::raise_null_reference_exception();
\n        }
\n        if (this_04 == (JAHPKOOJOGP *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n          uStack_30 = 0x18372040e;
\n          il2cpp::codegen::raise_null_reference_exception();
\n        }
\n        uStack_30 = 0x1837202f4;
\n        JAHPKOOJOGP::NCFKAPBGJEH(this_04,*(uint *)(lVar2 + 0x18));
\n        uStack_30 = 0x183720300;
\n        JAHPKOOJOGP::MJJKENEHAJJ(this_04,CFLNPMMIHLB);
\n        uStack_30 = 0x18372030e;
\n        JAHPKOOJOGP::PBOJINGFHNK(this_04,(undefined *)this_03,0);
\n        if ((CFLNPMMIHLB - 4 & 0xfffd) == 0) {
\n          bVar10 = true;
\n          *(undefined1 *)\n           ((longlong)&((NetworkManager *)this)->onGetValidDispatchSeverDataCallback + 3) = 0;
\n        }
\n        else {
\n          puVar3 = ((NetworkManager *)this)->client;
\n          if (puVar3 == (undefined *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n            uStack_30 = 0x183720408;
\n            il2cpp::codegen::raise_null_reference_exception();
\n          }
\n          iVar1 = *(int *)(puVar3 + 0x4c);
\n          *(uint *)(puVar3 + 0x4c) = iVar1 + 1U;
\n          uStack_30 = 0x183720347;
\n          JAHPKOOJOGP::HCLFHCFJGBJ(this_04,iVar1 + 1U);
\n          cVar5 = '\x01';
\n          if (*(char *)((longlong)&((NetworkManager *)this)->onGetValidDispatchSeverDataCallback +\n                       2) == '\0') {
\n            cVar5 = *(char *)((longlong)\n                              &((NetworkManager *)this)->onGetValidDispatchSeverDataCallback + 3);
\n          }
\n          bVar10 = cVar5 != '\0';
\n        }
\n        lVar2 = *_DAT_189ac29b8;
\n        if (*(char *)(lVar2 + 0x136) == '\0') {
\n          uStack_30 = 0x18372037d;
\n          FUN_18043e4c0(lVar2);
\n        }
\n        lVar2 = **(longlong **)(lVar2 + 0x90);
\n        if (*(char *)(lVar2 + 0x136) == '\0') {
\n          uStack_30 = 0x183720398;
\n          FUN_18043e4c0(lVar2);
\n        }
\n        if ((HGGCHKFCEBM *)**(undefined8 **)(lVar2 + 0x28) == (HGGCHKFCEBM *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n          uStack_30 = 0x183720402;
\n          il2cpp::codegen::raise_null_reference_exception();
\n        }
\n        uStack_30 = 0x1837203ac;
\n        bVar4 = HGGCHKFCEBM::MDCAPCIJPAK((HGGCHKFCEBM *)**(undefined8 **)(lVar2 + 0x28),this_04);
\n        if (bVar4 == 0) {
\n          uStack_30 = 0x1837203bb;
\n          NetworkManager::TryCacheSendPacket((NetworkManager *)this,this_04);
\n          if (bVar10) {
\n            if (((NetworkManager *)this)->GlobalDispatchData_k_BackingField == (undefined *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n              uStack_30 = 0x1837203fc;
\n              il2cpp::codegen::raise_null_reference_exception();
\n            }
\n            uStack_30 = 0x1837203dd;
\n            FUN_180260fe0(5,_DAT_189a1ccd0,\n                          ((NetworkManager *)this)->GlobalDispatchData_k_BackingField,this_04);
\n          }
\n        }
\n      }
\n    }
\n    return;
\n  }
\n  uStack_30 = 0x181ac5ae4;
\n  pIVar7 = IFix::WrappersManagerImpl::GetPatch(0x2865);
\n  if (pIVar7 == (ILFixDynamicMethodWrapper *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n    uStack_30 = 0x181ac5b16;
\n    il2cpp::codegen::raise_null_reference_exception();
\n  }
\n}
\nelse {
\n  uStack_30 = 0x1819c5f3a;
\n  pIVar7 = IFix::WrappersManagerImpl::GetPatch(0x108d7);
\n  if (pIVar7 == (ILFixDynamicMethodWrapper *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n    uStack_30 = 0x1819c5f66;
\n    il2cpp::codegen::raise_null_reference_exception();
\n  }
\n}
\nCStack_58.argumentBase = (undefined *)0x0;
\nCStack_58.evaluationStackBase = (undefined *)0x0;
\nCStack_58.managedStack = (undefined *)0x0;
\nCStack_58.currentTop = (undefined *)0x0;
\nCStack_58.topWriteBack = (undefined *)0x0;
\npCVar9 = IFix::Core::Call::Begin();
\nCStack_58.argumentBase = pCVar9->argumentBase;
\nCStack_58.evaluationStackBase = pCVar9->evaluationStackBase;
\nCStack_58.managedStack = pCVar9->managedStack;
\nCStack_58.currentTop = pCVar9->currentTop;
\nCStack_58.topWriteBack = pCVar9->topWriteBack;
\nif (pIVar7->anonObj != (undefined *)0x0) {
\n  IFix::Core::Call::PushObject(&CStack_58,pIVar7->anonObj);
\n}
\nIFix::Core::Call::PushObject(&CStack_58,(undefined *)this);
\nif ((VirtualMachine *)pIVar7->virtualMachine == (VirtualMachine *)0x0) {
\n                  /* WARNING: Subroutine does not return */\n  il2cpp::codegen::raise_null_reference_exception();
\n}
\nIFix::Core::VirtualMachine::Execute\n          ((VirtualMachine *)pIVar7->virtualMachine,pIVar7->methodId,&CStack_58,\n           (pIVar7->anonObj != (undefined *)0x0) + 1,0);
\nreturn;
\