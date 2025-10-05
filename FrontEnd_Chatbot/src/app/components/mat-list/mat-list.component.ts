import { Component, Input, OnChanges,Output, EventEmitter, SimpleChange, SimpleChanges } from '@angular/core';
import { MatListModule } from '@angular/material/list';
import { MatRadioModule } from '@angular/material/radio';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-mat-list',
  imports: [FormsModule, MatListModule, MatRadioModule, CommonModule, MatFormFieldModule, MatSelectModule],
  templateUrl: './mat-list.component.html',
  styleUrl: './mat-list.component.css'
})
export class MatListComponent implements OnChanges {
  @Input() field : any[] = [];
  @Output() formDataChanged = new EventEmitter<{ [key: string]: string }>();

  formData: { [key: string]: string} = {};
  types: string[] = [];
  values: string[] = [];
  name: string[] = [];
  required: boolean[] = [];
  
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['field']) {
      const normalized =  Array.isArray(this.field) ? this.field : [this.field];

      this.types = normalized.map(el => el.type);
      this.required = normalized.map(el => el.required)
      
      this.values = normalized.flatMap(el =>
         el.components.map((comp: any) => comp["values"])
      );

      this.name = normalized.map(el => el.name);

    }
  }

  getIndexes(n: number): number[] {
    return Array.from({ length: n }, (_, i) => i);
  }

  onListChange(label: string, value:string) {
    this.formData[label] = value;
    this.formDataChanged.emit({ [label]: value });
  }

}

