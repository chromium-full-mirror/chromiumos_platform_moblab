import { Component, OnInit } from '@angular/core';
import { ViewEncapsulation, ViewChild, ElementRef, PipeTransform, Pipe } from '@angular/core';
import { DomSanitizer } from "@angular/platform-browser";


@Pipe({ name: 'safe' })
export class MobmonitorPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) { }
  transform(url) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

@Component({
  selector: 'mob-mobmonitor',
  templateUrl: './mobmonitor.component.html',
  styleUrls: ['./mobmonitor.component.scss']
})
export class MobmonitorComponent {
  title = 'app';

  video = "http://localhost:9991"

}