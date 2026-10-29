// program: UserAssembly_slim.dll
// imageBase: 180000000
// functions in db: 26314

/* ================= 0x180432a60 ================= */
/* name   = FUN_180432a60 */
/* entry  = 180432a60 */
/* body   = 775 bytes */
/* sig    = undefined FUN_180432a60() */


undefined8 FUN_180432a60(undefined4 *param_1,char param_2)

{
  char cVar1;
  longlong lVar2;
  longlong lVar3;
  longlong lVar4;
  longlong lVar5;
  undefined8 local_res8;
  undefined8 uVar6;
  
  uVar6 = 0xfffffffffffffffe;
  FUN_1803f4990(&DAT_1899db6b0);
  lVar2 = FUN_18043b320(*param_1);
  if (lVar2 == 0) {
    if (param_2 != '\0') {
      uVar6 = FUN_1804303f0(DAT_1899db1c0,"System","NotSupportedException",
                            "IL2CPP encountered a managed type which it cannot convert ahead-of-time. The type uses generic or array types which are nested beyond the maximum depth which can be converted."
                            ,uVar6);
      FUN_180447cf0(uVar6,0);
      local_res8 = uVar6;
                    /* WARNING: Subroutine does not return */
      FUN_1804ff8e0(&local_res8,&DAT_188d08588);
    }
    FUN_1803f72c0(&DAT_1899db6b0);
    uVar6 = 0;
  }
  else {
    if (*(longlong *)(param_1 + 6) == 0) {
      lVar3 = FUN_1804f09a0(DAT_1899dbad0,1,(ulonglong)*(ushort *)(lVar2 + 0x120) * 0x10 + 0x148);
      if (lVar3 != 0) {
        FUN_180500080(lVar3,0,0x148);
        *(undefined8 *)(lVar3 + 200) = 0;
        *(undefined8 *)(lVar3 + 0xd0) = 0;
      }
      *(longlong *)(param_1 + 6) = lVar3;
      *(longlong *)lVar3 = lVar3;
      *(undefined8 *)(lVar3 + 0xa8) = *(undefined8 *)(lVar2 + 0xa8);
      *(undefined8 *)(lVar3 + 0x20) = *(undefined8 *)(lVar2 + 0x20);
      *(undefined8 *)(lVar3 + 0x58) = *(undefined8 *)(lVar2 + 0x58);
      *(undefined4 *)(lVar3 + 0x10c) = *(undefined4 *)(lVar2 + 0x10c);
      *(undefined4 **)(lVar3 + 0xc0) = param_1;
      lVar4 = FUN_18043b320(*param_1);
      lVar5 = *(longlong *)(lVar3 + 0xc0);
      if (*(longlong *)(lVar4 + 0x80) != 0) {
        uVar6 = FUN_1804ecb50(*(longlong *)(lVar4 + 0x80) + 0x60,lVar5 + 8,0);
        uVar6 = FUN_180430150(uVar6,1);
        *(undefined8 *)(lVar3 + 0x80) = uVar6;
      }
      if (*(longlong *)(lVar4 + 0x88) != 0) {
        uVar6 = FUN_1804ecb50(*(longlong *)(lVar4 + 0x88) + 0x60,lVar5 + 8,0);
        uVar6 = FUN_180430150(uVar6,1);
        *(undefined8 *)(lVar3 + 0x88) = uVar6;
      }
      *(undefined1 *)(lVar3 + 0x6a) = 0x15;
      *(undefined1 *)(lVar3 + 0xba) = 0x15;
      *(undefined4 **)(lVar3 + 0x60) = param_1;
      *(undefined4 **)(lVar3 + 0xb0) = param_1;
      *(uint *)(lVar3 + 0xb8) = *(uint *)(lVar3 + 0xb8) | 0x40000000;
      *(undefined2 *)(lVar3 + 0x128) = *(undefined2 *)(lVar2 + 0x128);
      *(undefined2 *)(lVar3 + 0x12a) = *(undefined2 *)(lVar2 + 0x12a);
      *(undefined2 *)(lVar3 + 300) = *(undefined2 *)(lVar2 + 300);
      *(undefined2 *)(lVar3 + 0x124) = *(undefined2 *)(lVar2 + 0x124);
      *(undefined2 *)(lVar3 + 0x126) = *(undefined2 *)(lVar2 + 0x126);
      *(undefined1 *)(lVar3 + 0x137) = *(undefined1 *)(lVar2 + 0x137);
      *(undefined1 *)(lVar3 + 0x142) = *(undefined1 *)(lVar2 + 0x142);
      *(longlong *)(lVar3 + 0x98) = lVar3;
      *(longlong *)(lVar3 + 0x30) = lVar3;
      cVar1 = *(char *)(lVar2 + 0x139);
      *(char *)(lVar3 + 0x139) = cVar1;
      *(uint *)(lVar3 + 0xe8) = (uint)(cVar1 == '\0');
      *(undefined1 *)(lVar3 + 0x13b) = *(undefined1 *)(lVar2 + 0x13b);
      *(undefined4 *)(lVar3 + 0x118) = 0xffffffff;
      *(undefined4 *)(lVar3 + 0x100) = 0xffffffff;
      *(undefined4 *)(lVar3 + 0xf8) = *(undefined4 *)(lVar2 + 0xf8);
      uVar6 = FUN_180436810();
      *(undefined8 *)(lVar3 + 0x48) = uVar6;
      if (*(undefined4 **)(lVar3 + 0xc0) != (undefined4 *)0x0) {
        lVar5 = FUN_18043b320(**(undefined4 **)(lVar3 + 0xc0));
        if (lVar5 == DAT_1899db360) {
          uVar6 = FUN_180430150(**(undefined8 **)
                                  (*(longlong *)(*(longlong *)(lVar3 + 0xc0) + 8) + 8),1);
          *(undefined8 *)(lVar3 + 0x98) = uVar6;
          *(undefined8 *)(lVar3 + 0x30) = uVar6;
        }
      }
      if (*(char *)(lVar3 + 0x137) != '\0') {
        uVar6 = *(undefined8 *)(lVar2 + 0x30);
        *(undefined8 *)(lVar3 + 0x98) = uVar6;
        *(undefined8 *)(lVar3 + 0x30) = uVar6;
      }
      *(undefined1 *)(lVar3 + 0x141) = *(undefined1 *)(lVar2 + 0x141);
    }
    uVar6 = *(undefined8 *)(param_1 + 6);
    FUN_1803f72c0(&DAT_1899db6b0);
  }
  return uVar6;
}



/* ================= 0x18042fe20 ================= */
/* name   = FUN_18042fe20 */
/* entry  = 18042fe20 */
/* body   = 802 bytes */
/* sig    = undefined FUN_18042fe20() */


ulonglong FUN_18042fe20(uint *param_1)

{
  byte bVar1;
  undefined4 uVar2;
  ulonglong uVar3;
  ulonglong uVar4;
  undefined8 uVar5;
  int iVar6;
  ulonglong *puVar7;
  ulonglong uVar8;
  ulonglong uVar9;
  longlong *plVar10;
  ulonglong *puVar11;
  longlong lVar12;
  ulonglong *puVar13;
  uint uVar14;
  int iVar15;
  undefined8 local_60;
  ulonglong local_58;
  undefined1 local_50 [24];
  
  FUN_1803f4990(&DAT_1899db6b0);
  uVar4 = *(ulonglong *)(param_1 + 2);
  uVar9 = DAT_1899db658 & uVar4;
  puVar13 = (ulonglong *)0x0;
  iVar15 = 0;
  uVar8 = DAT_1899db658;
  puVar11 = puVar13;
  do {
    lVar12 = (uVar9 >> 6) * 0x20;
    plVar10 = (longlong *)(DAT_1899db678 + lVar12);
    uVar3 = 1L << ((byte)uVar9 & 0x3f);
    if ((plVar10[1] & uVar3) == 0) {
      lVar12 = DAT_1899db668;
      puVar7 = puVar13;
      if (((plVar10[2] & uVar3) == 0) || (DAT_1899db680 <= puVar11)) goto LAB_18042ff01;
    }
    else {
      bVar1 = FUN_180415ac0(uVar3 - 1 & plVar10[1]);
      puVar7 = (ulonglong *)((ulonglong)bVar1 * 0x10 + *plVar10);
      uVar8 = DAT_1899db658;
      if (uVar4 == *puVar7) {
        lVar12 = lVar12 + DAT_1899db660;
LAB_18042ff01:
        if (((lVar12 - DAT_1899db660 & 0xffffffffffffffe0U) + DAT_1899db660 == DAT_1899db668) &&
           (puVar7 == (ulonglong *)0x0)) {
          uVar4 = FUN_1804f09a0(DAT_1899dbad0,1,0x148);
          if (uVar4 != 0) {
            FUN_180500080(uVar4,0,0x148);
            *(undefined8 *)(uVar4 + 200) = 0;
            *(undefined8 *)(uVar4 + 0xd0) = 0;
          }
          *(ulonglong *)uVar4 = uVar4;
          uVar5 = FUN_18043ab50(*(int *)(*(longlong *)(param_1 + 2) + 4) + 0xee50a144U ^ *param_1);
          *(undefined8 *)(uVar4 + 0xa8) = uVar5;
          *(undefined1 **)(uVar4 + 0x20) = &DAT_187aebda5;
          uVar14 = (uint)*(undefined8 *)param_1 ^ **(uint **)(param_1 + 2) ^ 0x6fe8ee1b;
          if (uVar14 != 0xffffffff) {
            iVar15 = ((uint)((((ulonglong)uVar14 * 0x6ae9 ^ 0x2e6f3e3d) * 0x2ad3dd28 >> 0x16) *
                             0x4c39b37d >> 10) ^ 0x4dfaa6b0) * 0x22449c6e;
            puVar13 = (ulonglong *)
                      ((ulonglong)uVar14 * 0x10 + (int)(DAT_188198e00 ^ 0x7497c9ee) + DAT_1899dbaf8)
            ;
          }
          if (*(int *)((longlong)puVar13 + 0xc) + -0x175a3fdf == iVar15) {
            lVar12 = FUN_18043b320((*(int *)((longlong)puVar13 + 4) + -0x1df344f8) - iVar15);
          }
          else {
            plVar10 = (longlong *)FUN_180437120();
            lVar12 = *plVar10;
          }
          *(undefined8 *)(uVar4 + 0x58) = *(undefined8 *)(lVar12 + 0x58);
          *(undefined1 *)(uVar4 + 0x13f) = 1;
          *(bool *)(uVar4 + 0x136) = *(char *)(uVar4 + 0x13d) == '\0';
          *(undefined8 *)(uVar4 + 0x80) = DAT_1899db1c8;
          *(ulonglong *)(uVar4 + 0x30) = uVar4;
          *(ulonglong *)(uVar4 + 0x98) = uVar4;
          *(undefined4 *)(uVar4 + 0x10c) = 1;
          iVar6 = 0x13;
          if (*(int *)((longlong)puVar13 + 0xc) + -0x175a3fdf != iVar15) {
            iVar6 = 0x1e;
          }
          *(uint *)(uVar4 + 0x68) = iVar6 << 0x10 | *(uint *)(uVar4 + 0x68) & 0xff00ffff;
          *(char *)(uVar4 + 0xba) = (char)iVar6;
          uVar2 = (undefined4)
                  (*(longlong *)(param_1 + 2) - ((DAT_188198e40 + -0x77870e75) + DAT_1899dbaf8) >> 4
                  );
          *(undefined4 *)(uVar4 + 0x60) = uVar2;
          *(undefined4 *)(uVar4 + 0xb0) = uVar2;
          *(uint *)(uVar4 + 0xb8) = *(uint *)(uVar4 + 0xb8) | 0x40000000;
          *(undefined4 *)(uVar4 + 0x114) = 8;
          *(undefined8 *)(uVar4 + 0x100) = 0xffffffffffffffff;
          *(undefined1 *)(uVar4 + 0x138) = 1;
          *(undefined1 *)(uVar4 + 0x132) = 1;
          local_60 = *(undefined8 *)(param_1 + 2);
          local_58 = uVar4;
          FUN_18041fc70(&DAT_1899db650,local_50,&local_60,&local_60);
        }
        else {
          uVar4 = puVar7[1];
        }
        FUN_1803f72c0(&DAT_1899db6b0);
        return uVar4;
      }
    }
    puVar11 = (ulonglong *)((longlong)puVar11 + 1);
    uVar9 = uVar9 + (longlong)puVar11 & uVar8;
  } while( true );
}



/* ================= 0x18043b320 ================= */
/* name   = FUN_18043b320 */
/* entry  = 18043b320 */
/* body   = 148 bytes */
/* sig    = undefined FUN_18043b320() */


undefined8 FUN_18043b320(int param_1)

{
  longlong lVar1;
  undefined8 uVar2;
  
  if (param_1 == -1) {
    uVar2 = 0;
  }
  else {
    lVar1 = (longlong)param_1 * 8;
    if (*(longlong *)(lVar1 + DAT_1899dbbf0) == 0) {
      FUN_1803f4990(&DAT_1899db6b0);
      if (*(longlong *)(lVar1 + DAT_1899dbbf0) == 0) {
        uVar2 = FUN_180430980(param_1);
        *(undefined8 *)(lVar1 + DAT_1899dbbf0) = uVar2;
      }
      FUN_1803f72c0(&DAT_1899db6b0);
    }
    uVar2 = *(undefined8 *)(lVar1 + DAT_1899dbbf0);
  }
  return uVar2;
}



