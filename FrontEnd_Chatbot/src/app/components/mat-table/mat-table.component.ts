import { Component, Input, OnChanges, SimpleChanges } from "@angular/core";
import { MatTableModule } from "@angular/material/table";
import { CommonModule } from "@angular/common";

@Component({
  selector: 'app-mat-table',
  imports: [CommonModule, MatTableModule],
  templateUrl: './mat-table.component.html',
  styleUrl: './mat-table.component.css',
})
export class MatTableComponent implements OnChanges {
  @Input() tabella!: any;

  displayedColumns: string[] = [];
  dataSource: any[] = [];

  ngOnChanges(changes: SimpleChanges): void {
    console.log(typeof this.tabella)
    if (changes['tabella'] && this.tabella && this.tabella.components) {
      const headerRow = this.tabella.components.find((r: any) => r.name === 'Header');
      const dataRows = this.tabella.components.filter((r: any) => r.name !== 'Header');

      if (headerRow) {
        this.displayedColumns = headerRow.components.map((c: any) => c.name);

        this.dataSource = dataRows.map((riga: any) => {
          const obj: any = {};
          riga.components.forEach((cella: any, i: number) => {
            obj[this.displayedColumns[i]] = cella.name;
          });
          return obj;
        });
      }
    }
  }
}
