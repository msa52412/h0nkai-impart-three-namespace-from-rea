
byte bVar1;
int iVar2;
longlong lVar3;
undefined *puVar4;
undefined8 uVar5;
RectTransform *pRVar6;
ILFixDynamicMethodWrapper *this_00;
undefined8 uVar7;
float x;
float y;
float alpha;
float time;
GradientAlphaKey GStack_78;
Vector3 aVStack_70 [2];
Vector3 aVStack_58 [6];

bVar1 = IFix::WrappersManagerImpl::IsPatched(0x9bc0);
if (bVar1 != 0) {
  this_00 = IFix::WrappersManagerImpl::GetPatch(0x9bc0);
  if (this_00 != (ILFixDynamicMethodWrapper *)0x0) {
    IFix::ILFixDynamicMethodWrapper::Gen_Wrap_15
              ((ILFixDynamicMethodWrapper_57479 *)this_00,(undefined *)this,(undefined *)img,
               (undefined *)itemBase,isMainDrop);
    return;
  }
                  /* WARNING: Subroutine does not return */
  il2cpp::codegen::raise_null_reference_exception();
}
lVar3 = thunk_FUN_180442320(itemBase,_DAT_189a18318);
if (isMainDrop == 0) {
  if (lVar3 == 0) {
    if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
      il2cpp::codegen::runtime_class_init();
    }
    puVar4 = ExcelMeta::ConstValueDataReaderExtend::get_DefaultGachaGiftDropDisplayConfig();
    goto LAB_1825e1f63;
  }
  lVar3 = thunk_FUN_180442320(itemBase,_DAT_189a18318);
  if (lVar3 == 0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  uVar5 = thunk_FUN_180442320(itemBase,_DAT_189a18318);
  uVar7 = 1;
}
else {
  if (lVar3 == 0) {
    if (*(int *)(_DAT_189a15480 + 0xe8) == 0) {
      il2cpp::codegen::runtime_class_init();
    }
    puVar4 = ExcelMeta::ConstValueDataReaderExtend::get_DefaultGachaMainDropDisplayConfig();
    goto LAB_1825e1f63;
  }
  lVar3 = thunk_FUN_180442320(itemBase,_DAT_189a18318);
  if (lVar3 == 0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  uVar5 = thunk_FUN_180442320(itemBase,_DAT_189a18318);
  uVar7 = 0;
}
puVar4 = (undefined *)FUN_180257840(uVar7,_DAT_189a18318,uVar5);
LAB_1825e1f63:
if ((puVar4 != (undefined *)0x0) && (iVar2 = FUN_180257840(0,_DAT_189a18320,puVar4), iVar2 == 4))
{
  x = (float)FUN_1803675a0(0,_DAT_189a18328,puVar4,0);
  y = (float)FUN_1803675a0(0,_DAT_189a18328,puVar4,1);
  alpha = (float)FUN_1803675a0(0,_DAT_189a18328,puVar4,2);
  time = (float)FUN_1803675a0(0,_DAT_189a18328,puVar4,3);
  if (img == (Image *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  pRVar6 = UnityEngine::UI::Graphic::get_rectTransform((Graphic *)img);
  aVStack_70[0].x = 0.0;
  aVStack_70[0].y = 0.0;
  aVStack_70[0].z = 0.0;
  UnityEngine::Vector3::_ctor(aVStack_70,x,y,0.0);
  if (pRVar6 == (RectTransform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  aVStack_58[0].x = aVStack_70[0].x;
  aVStack_58[0].y = aVStack_70[0].y;
  aVStack_58[0].z = aVStack_70[0].z;
  UnityEngine::Transform::set_localPosition((Transform *)pRVar6,aVStack_58);
  pRVar6 = UnityEngine::UI::Graphic::get_rectTransform((Graphic *)img);
  GStack_78.alpha = 0.0;
  GStack_78.time = 0.0;
  UnityEngine::GradientAlphaKey::_ctor(&GStack_78,alpha,time);
  if (pRVar6 == (RectTransform *)0x0) {
                  /* WARNING: Subroutine does not return */
    il2cpp::codegen::raise_null_reference_exception();
  }
  UnityEngine::RectTransform::set_sizeDelta(pRVar6,(Vector2)GStack_78);
}
return;\