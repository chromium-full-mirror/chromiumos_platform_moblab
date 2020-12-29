import {fromEvent as observableFromEvent} from 'rxjs';

import {takeUntil, finalize, map, mergeMap, skipUntil} from 'rxjs/operators';
import {
  Component,
  ElementRef,
  Input,
  Output,
  EventEmitter,
  AfterViewInit,
  ViewChild,
  OnChanges,
} from '@angular/core';
import {FeedbackService} from '../feedback.service';

@Component({
  selector: 'feedback-toolbar',
  templateUrl: './feedback-toolbar.component.html',
  styleUrls: ['./feedback-toolbar.component.css'],
})
export class FeedbackToolbarComponent implements AfterViewInit, OnChanges {
  @Input()
  public drawColor: string;
  @Output()
  public manipulate = new EventEmitter<string>();
  public disableToolbarTips = false;
  @ViewChild('toggleMove')
  private toggleMoveBtn: ElementRef;
  public isSwitch = false;
  public isDragging = false;
  public vars: object = {};

  constructor(public el: ElementRef, private feedbackService: FeedbackService) {
    this.vars = feedbackService.initialVariables;
  }

  public ngAfterViewInit() {
    const elStyle = this.el.nativeElement.style;
    elStyle.position = 'absolute';
    elStyle.left = '43%';
    elStyle.top = '60%';
    this.addDragListenerOnMoveBtn();
  }

  public ngOnChanges() {
    this.isSwitch = this.drawColor !== this.feedbackService.highlightedColor;
  }

  public done() {
    this.manipulate.emit('done');
  }

  public toggleHighlight() {
    this.isSwitch = false;
    this.manipulate.emit(this.feedbackService.highlightedColor);
  }

  public toggleHide() {
    this.isSwitch = true;
    this.manipulate.emit(this.feedbackService.hiddenColor);
  }

  public addDragListenerOnMoveBtn() {
    const mouseDown$ = observableFromEvent<MouseEvent>(
      this.toggleMoveBtn.nativeElement,
      'mousedown'
    );
    const mouseUp$ = observableFromEvent<MouseEvent>(
      this.toggleMoveBtn.nativeElement,
      'mouseup'
    );
    const mouseMove$ = observableFromEvent<MouseEvent>(
      this.toggleMoveBtn.nativeElement,
      'mousemove'
    );

    //Mouse drag event
    const mouseDragging$ = mouseMove$.pipe(
      skipUntil(mouseDown$),
      takeUntil(mouseUp$)
    );
    const move$ = mouseDragging$.pipe(
      mergeMap((md: MouseEvent, index: number) => {
        this.feedbackService.setIsDraggingToolbar(true);
        const startX = md.offsetX;
        const startY = md.offsetY;
        this.disableToolbarTips = true;
        this.isDragging = true;
        // Calculate dif with mousemove until mouseup
        return mouseMove$.pipe(
          map((mm: MouseEvent) => {
            mm.preventDefault();
            return {
              left: mm.clientX - startX,
              top: mm.clientY - startY,
            };
          }),
          finalize(() => {
            this.isDragging = false;
            this.disableToolbarTips = false;
            this.feedbackService.setIsDraggingToolbar(false);
          }),
          takeUntil(mouseUp$)
        );
      })
    );
    move$.subscribe((pos: {left: number; top: number}) => {
      this.el.nativeElement.style.left = pos.left + 'px';
      this.el.nativeElement.style.top = pos.top + 'px';
    });
  }
}
