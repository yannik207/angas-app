import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  inject,
  input,
  output,
  signal,
  viewChild,
} from '@angular/core';
import { Shift } from '../../models/shift.model';

/** A shift action emitted by the menu. Add new ids here to grow the menu. */
export type ShiftAction = 'details' | 'edit' | 'assign' | 'delete';

interface ShiftMenuItem {
  action: ShiftAction;
  label: string;
  danger?: boolean;
}

/**
 * Small per-shift options menu (kebab trigger + dropdown).
 * New adjustments can be added by extending MENU_ITEMS and the `action` output.
 */
const MENU_ITEMS: ShiftMenuItem[] = [
  { action: 'details', label: 'Details' },
  { action: 'edit', label: 'Edit' },
  { action: 'assign', label: 'Assign staff' },
  { action: 'delete', label: 'Delete', danger: true },
];

@Component({
  selector: 'app-shift-menu',
  templateUrl: './shift-menu.html',
  styleUrl: './shift-menu.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '[class.shift-menu--sm]': "size() === 'sm'",
    '(document:keydown.escape)': 'close()',
  },
})
export class ShiftMenu {
  readonly shift = input.required<Shift>();
  readonly size = input<'sm' | 'md'>('md');

  readonly action = output<{ action: ShiftAction; shift: Shift }>();

  readonly items = MENU_ITEMS;
  readonly open = signal(false);
  readonly menuTop = signal(0);
  readonly menuLeft = signal(0);

  private readonly trigger = viewChild.required<ElementRef<HTMLButtonElement>>('trigger');
  private readonly hostRef = inject<ElementRef<HTMLElement>>(ElementRef);

  private readonly onDocClick = (e: MouseEvent): void => {
    if (!this.hostRef.nativeElement.contains(e.target as Node)) this.close();
  };
  private readonly onReposition = (): void => this.close();

  constructor() {
    inject(DestroyRef).onDestroy(() => this.detachListeners());
  }

  toggle(event: MouseEvent): void {
    event.stopPropagation();
    if (this.open()) {
      this.close();
    } else {
      this.openMenu();
    }
  }

  select(event: MouseEvent, action: ShiftAction): void {
    event.stopPropagation();
    this.action.emit({ action, shift: this.shift() });
    this.close();
  }

  close(): void {
    if (!this.open()) return;
    this.open.set(false);
    this.detachListeners();
  }

  private openMenu(): void {
    const rect = this.trigger().nativeElement.getBoundingClientRect();
    const width = 160;
    const estHeight = 8 + this.items.length * 36;

    let left = Math.min(rect.right - width, window.innerWidth - width - 8);
    left = Math.max(8, left);

    let top = rect.bottom + 4;
    if (top + estHeight > window.innerHeight - 8) {
      top = Math.max(8, rect.top - estHeight - 4);
    }

    this.menuLeft.set(left);
    this.menuTop.set(top);
    this.open.set(true);

    // Capture phase so we also catch scrolls inside the calendar's scroll container.
    document.addEventListener('click', this.onDocClick, true);
    window.addEventListener('scroll', this.onReposition, true);
    window.addEventListener('resize', this.onReposition, true);
  }

  private detachListeners(): void {
    document.removeEventListener('click', this.onDocClick, true);
    window.removeEventListener('scroll', this.onReposition, true);
    window.removeEventListener('resize', this.onReposition, true);
  }
}
