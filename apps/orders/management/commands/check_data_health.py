"""Kaynak satırlar ve hesap defterindeki anormallikleri değiştirmeden raporla."""

import json
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from apps.orders.models import FinancialLine, OrderLine
from apps.orders.services import rule_version


class Command(BaseCommand):
    help = "Negatif ücret, yüksek kâr marjı, geçersiz kur ve eksik hesap defterini tarar."

    def add_arguments(self, parser):
        parser.add_argument("--store", type=int, help="Yalnız bu mağaza kimliğini tara.")
        parser.add_argument("--json", action="store_true", help="Sonucu JSON olarak yaz.")
        parser.add_argument(
            "--fail-on-findings", action="store_true", help="Bulgu varsa exit 1 dön."
        )

    def handle(self, *args, **options):
        query = OrderLine.objects.select_related("store", "financial").order_by("pk")
        if options["store"] is not None:
            query = query.filter(store_id=options["store"])
        findings = []
        checked = 0
        for line in query.iterator():
            checked += 1
            codes = []
            if line.exchange_rate <= 0 or (line.currency == "TRY" and line.exchange_rate != 1):
                codes.append("invalid_exchange_rate")
            if not Decimal("0") <= line.commission_percent <= Decimal("100"):
                codes.append("invalid_commission_rate")
            if line.returned_quantity > line.quantity:
                codes.append("invalid_return_quantity")
            if line.seller_discount + line.platform_coupon > line.unit_price_gross * line.quantity:
                codes.append("discount_exceeds_gross")
            try:
                ledger = line.financial
            except FinancialLine.DoesNotExist:
                codes.append("missing_ledger")
            else:
                if any(
                    getattr(ledger, name) < 0
                    for name in (
                        "commission",
                        "shipping",
                        "service",
                        "cost",
                        "withholding",
                        "fee_vat",
                        "cost_vat",
                    )
                ):
                    codes.append("negative_fee_or_cost")
                if ledger.net_sales > 0 and ledger.profit * 100 > ledger.net_sales * 90:
                    codes.append("profit_margin_above_90_percent")
                if ledger.rule_version != rule_version(line.store):
                    codes.append("outdated_rule_version")
                if ledger.gross_sales != ledger.net_sales + ledger.sales_vat:
                    codes.append("vat_split_mismatch")
            if codes:
                findings.append({"line_id": line.pk, "store_id": line.store_id, "codes": codes})
        report = {"checked_lines": checked, "finding_count": len(findings), "findings": findings}
        if options["json"]:
            self.stdout.write(json.dumps(report, ensure_ascii=False))
        else:
            self.stdout.write(f"{checked} satır tarandı; {len(findings)} anormallik bulundu.")
            for finding in findings:
                self.stdout.write(
                    f"Satır {finding['line_id']} / mağaza {finding['store_id']}: "
                    + ", ".join(finding["codes"])
                )
        if findings and options["fail_on_findings"]:
            raise CommandError(f"{len(findings)} anormallik bulundu.")
