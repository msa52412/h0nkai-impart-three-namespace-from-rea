
longlong lVar1;
StorageDataItemBase *storageItem;
BaseMonoCanvas *this_00;
byte bVar2;
SecurityParser *this_01;
undefined *puVar3;
undefined *nodeName;
Transform *pTVar4;
Object *x;
longlong lVar5;
SmallXmlParser *parser;
KeyGeneratedEventHandler *this_02;
ILFixDynamicMethodWrapper *this_03;
undefined8 in_RDX;
uint uVar6;
longlong lVar7;
longlong lVar8;
StringKey SStackX_10;
uint uStackX_18;

SStackX_10.hash = 0;
bVar2 = IFix::WrappersManagerImpl::IsPatched(0x1626c);
if (bVar2 != 0) {
  this_03 = IFix::WrappersManagerImpl::GetPatch(0x1626c);
  if (this_03 != (ILFixDynamicMethodWrapper *)0x0) {
    IFix::ILFixDynamicMethodWrapper::Gen_Wrap_13(this_03,(undefined *)this);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (this->dropItemPrefabPathDict == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(int *)(this->dropItemPrefabPathDict + 0x18) <= *(int *)&this->gotItemList) {
  (**(code **)(this->__klass + 0x268))(this,*(undefined8 *)(this->__klass + 0x270));
  lVar1 = *_DAT_189a985c0;
  if (*(char *)(lVar1 + 0x136) == '\0') {
    FUN_18043e4c0(lVar1);
  }
  lVar1 = **(longlong **)(lVar1 + 0x90);
  if (*(char *)(lVar1 + 0x136) == '\0') {
    FUN_18043e4c0(lVar1);
  }
  if ((MainUIManager *)**(undefined8 **)(lVar1 + 0x28) != (MainUIManager *)0x0) {
    MainUIManager::LockPage((MainUIManager *)**(undefined8 **)(lVar1 + 0x28),1,_DAT_187975ba0);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
DestroyAllTimer(this);
if (*(LNFBAFMHDEH **)&this->curShowIdx == (LNFBAFMHDEH *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
LNFBAFMHDEH::ACCLCBPEDAJ(*(LNFBAFMHDEH **)&this->curShowIdx);
puVar3 = this->dropItemPrefabPathDict;
uVar6 = *(uint *)&this->gotItemList;
if (puVar3 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
if (*(uint *)(puVar3 + 0x18) <= uVar6) {
  System::ThrowHelper::ThrowArgumentOutOfRangeException();
}
parser = (SmallXmlParser *)CONCAT71((int7)((ulonglong)in_RDX >> 8),1);
lVar1 = *(longlong *)(*(longlong *)(puVar3 + 0x10) + 0x20 + (longlong)(int)uVar6 * 8);
*(int *)&this->gotItemList = *(int *)&this->gotItemList + 1;
ExtensionMethods::DestroyChildren(this->itemsRoot,parser,0);
if (lVar1 == 0) {
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
lVar7 = 0x20;
lVar8 = 0x20;
uVar6 = 0;
do {
  if (*(int *)(lVar1 + 0x18) <= (int)uVar6) {
    if ((Animation *)this->showAnim == (Animation *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    UnityEngine::Animation::Rewind((Animation *)this->showAnim);
    if ((Animation *)this->showAnim != (Animation *)0x0) {
      UnityEngine::Animation::Play((Animation *)this->showAnim);
      return;
    }
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  this_01 = (SecurityParser *)il2cpp::codegen::object_new(_DAT_189a3c320);
  Mono::Xml::SecurityParser::probe_1826b9250(this_01,parser);
  if (this_01 == (SecurityParser *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  this_01->reader = (undefined *)this;
  if (*(uint *)(lVar1 + 0x18) <= uVar6) {
    System::ThrowHelper::ThrowArgumentOutOfRangeException();
  }
  lVar5 = *(longlong *)(*(longlong *)(lVar1 + 0x10) + lVar8);
  if (lVar5 == 0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  storageItem = *(StorageDataItemBase **)(lVar5 + 0x10);
  puVar3 = GetItemIconPrefabPath(this,storageItem);
  SStackX_10.hash = uVar6 + 1;
  uStackX_18 = SStackX_10.hash;
  nodeName = (undefined *)System::Int32::ToString(&SStackX_10);
  pTVar4 = BaseContext::SafeSyncCreateUniqueNode
                     ((BaseContext *)this,puVar3,nodeName,_DAT_189bb3608,1);
  this_01->handler = (undefined *)pTVar4;
  UnityEngine::ComponentExtensions::SafeSetActive(pTVar4,1);
  x = (Object *)FUN_183478cd0(this,this_01->handler,0,1,_DAT_189aee830);
  bVar2 = UnityEngine::Object::op_Inequality(x,(Object *)0x0);
  if (bVar2 != 0) {
    if (x == (Object *)0x0) {
                  /* WARNING: Subroutine does not return */
      il2cpp::codegen::raise_null_reference_exception();
    }
    (**(code **)(x->__klass + 0x288))(x,storageItem,*(undefined8 *)(x->__klass + 0x290));
  }
  parser = _DAT_189a15a70;
  lVar5 = func_0x000180257760(storageItem);
  if (lVar5 == 0) {
    parser = _DAT_189a18338;
    lVar5 = func_0x000180257760(storageItem);
    if (lVar5 == 0) {
      lVar5 = FUN_180261460(_DAT_189a985c0);
      if (lVar5 == 0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      puVar3 = this->DROP_ITEM_PREFAB_PATH;
      this_00 = *(BaseMonoCanvas **)(lVar5 + 0x10);
      if (puVar3 == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      if (*(uint *)(puVar3 + 0x18) <= uVar6) {
        System::ThrowHelper::ThrowArgumentOutOfRangeException();
      }
      if (this_00 == (BaseMonoCanvas *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      parser = (SmallXmlParser *)
               BaseMonoCanvas::CreateTimer
                         (this_00,*(float *)(lVar7 + *(longlong *)(puVar3 + 0x10)),0.0);
      this_02 = (KeyGeneratedEventHandler *)il2cpp::codegen::object_new(_DAT_1899defb0);
      KeyGeneratedEventHandler::_ctor(this_02,(undefined *)this_01,_DAT_189aee838);
      if (parser == (SmallXmlParser *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      parser->reader = (undefined *)this_02;
      CanvasTimer::StartRun((CanvasTimer *)parser,0);
      if (this->delayTimerSpanList == (undefined *)0x0) {
                  /* WARNING: Subroutine does not return */
        il2cpp::codegen::raise_null_reference_exception();
      }
      FUN_184c69c50(this->delayTimerSpanList,parser,_DAT_189ab27b8);
    }
  }
  lVar8 = lVar8 + 8;
  lVar7 = lVar7 + 4;
  uVar6 = uStackX_18;
} while( true );\