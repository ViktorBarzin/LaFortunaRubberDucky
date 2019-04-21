/*This file is prepared for Doxygen automatic documentation generation.*/
//! \file *********************************************************************
//!
//! \brief This file manages the keyboard task.
//!
//! - Compiler:           IAR EWAVR and GNU GCC for AVR
//! - Supported devices:  AT90USB1287, AT90USB1286, AT90USB647, AT90USB646
//!
//! \author               Atmel Corporation: http://www.atmel.com \n
//!                       Support and FAQ: http://support.atmel.no/
//!
//! ***************************************************************************
/* Copyright (c) 2009 Atmel Corporation. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * 3. The name of Atmel may not be used to endorse or promote products derived
 * from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with an Atmel
 * AVR product.
 *
 * THIS SOFTWARE IS PROVIDED BY ATMEL "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE EXPRESSLY AND
 * SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL ATMEL BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 * THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
//_____  I N C L U D E S ___________________________________________________
#include "config.h"
#include "conf_usb.h"
#include "keyboard_task.h"
#include "lib_board/stk_525/stk_525.h"
#include "lib_mcu/usb/usb_drv.h"
#include "usb_descriptors.h"
#include "modules/usb/device_chap9/usb_standard_request.h"
#include "lib_mcu/power/power_drv.h"
#include <util/delay.h>
//_____ D E F I N I T I O N S ______________________________________________
// start of escape keys.
// if key_to_send > ESCAPE_KEY_START then the next
// (key_to_send - ESCAPE_KEY_START) keys are treated as modifiers
#define ESCAPE_KEY_START 251
// this key (KEY_MEDIA_COFFEE not used I presume) is used to sleep.
// Amount of sleep in ms is a multiple of SLEEP_MS.
// The multiple is the next key read.
// E.g: if we read SLEEP_KEY, we read next_key and sleep (next_key * SLEEP_MS)
#define SLEEP_KEY 249
#define SLEEP_MS 100
const U8 code usb_keys[] = {HID_ENTER, SLEEP_KEY, 30, ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_GUI, HID_R, SLEEP_KEY, 5, HID_N, HID_O, HID_T, HID_E, HID_P, HID_A, HID_D, SLEEP_KEY, 5, HID_ENTER, SLEEP_KEY, 27, HID_CAPS_LOCK, HID_H, HID_CAPS_LOCK, HID_E, HID_L, HID_L, HID_O, HID_SPACEBAR, HID_CAPS_LOCK, HID_W, HID_CAPS_LOCK, HID_O, HID_R, HID_L, HID_D, ESCAPE_KEY_START + 1, HID_MODIFIER_LEFT_SHIFT, HID_1, HID_ENTER};
#define SIZEOF_USB_KEYS     (Uint16)sizeof(usb_keys)
#define myabs(n)  ((n) < 0 ? -(n) : (n))
//_____ D E C L A R A T I O N S ____________________________________________
volatile U8    cpt_sof;
U8    transmit_no_key;
volatile bit   key_hit;
U8    usb_key;
U8    usb_kbd_state;
U16   usb_data_to_send;
#ifdef __GNUC__
PGM_VOID_P     usb_key_pointer;
#else
U8   code *    usb_key_pointer;
#endif
void process_key(void);
void sendNothing(void);
//! This function initializes the hardware/software ressources required for keyboard task.
//!
void keyboard_task_init(void)
{
  // return;
  transmit_no_key   = FALSE;
  key_hit           = FALSE;
  usb_kbd_state     = 0;
  // Joy_init();
  cpt_sof           = 0;
}
//! @brief Entry point of the mouse management
//! This function links the mouse and the USB bus.
//!
void keyboard_task(void)
{
  if(Is_device_enumerated())
  {
    // if USB ready to transmit new data :
    //        - if last time = 0, nothing
    //        - if key pressed -> transmit key
    //        - if !key pressed -> transmit 0
    if (key_hit==FALSE)
    {
      kbd_test_hit();
    }
    else
    {
      Usb_select_endpoint(EP_KBD_IN);
      if(Is_usb_write_enabled())
      {
        if ( transmit_no_key==FALSE)
        {
          process_key();
          // transmit_no_key = TRUE;
          // Usb_write_byte(HID_MODIFIER_LEFT_ALT);  // Byte0: Modifier
          // // Usb_write_byte(HID_MODIFIER_NONE);  // Byte0: Modifier
          // Usb_write_byte(0);                  // Byte1: Reserved
          // // Usb_write_byte(usb_key);            // Byte2: Keycode 0
          // Usb_write_byte(HID_TAB);                  // Byte2: Keycode 1
          // Usb_write_byte(0);                  // Byte2: Keycode 2
          // Usb_write_byte(0);                  // Byte2: Keycode 3
          // Usb_write_byte(0);                  // Byte2: Keycode 4
          // Usb_write_byte(0);                  // Byte2: Keycode 5
          // Usb_send_in();
          return;
        }
        else
        {
          sendNothing();
          // key_hit = FALSE;
          // transmit_no_key = FALSE;
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_write_byte(0);
          // Usb_send_in();
        }
      }
    }
  }
}
void sendNothing(void) {
  key_hit = FALSE;
  transmit_no_key = FALSE;
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_write_byte(0);
  Usb_send_in();
}
int modifierKeysToRead = 0;
U16 modifier = HID_MODIFIER_NONE;
bool shouldSleep = false;
// This function processes the pressed key and sends it accordingly
// keys that are negative signal that the following key should be treated as a
// modifier keys. E.g: if usb_key is -2 this means that the next 2 keys should
// be treated as modifiers. If usb_key is positive, just send it.
void process_key(void) {
  transmit_no_key = TRUE;
  // if we have to sleep
  if (shouldSleep) {
    // sleep SLEEP_MS * current read key value
    // avr requires sleeping a compile-time constant int value. so loop
    // `usb_key` times
    // https://www.avrfreaks.net/forum/error-1-builtinavrdelaycycles-expects-integer-constant
    for (int i = 0; i < usb_key; i++) {
      _delay_ms(SLEEP_MS);
    }
    shouldSleep = false;
    return;
  } else if (usb_key == SLEEP_KEY) {
    shouldSleep = true;
    return;
  }
  if (usb_key > ESCAPE_KEY_START) {
    // start reading modifiers
    // set number of keys to read that should be treated as modifers
    modifierKeysToRead = usb_key;
    // modifierKeysToRead = 1;
    // reset modifier counter and modifier bits
    modifier = HID_MODIFIER_NONE;
    // sendNothing();
    return;
  }
  else {
    // if read key should be treated as modifier, OR it with modifier
    if (modifierKeysToRead > ESCAPE_KEY_START) {
      modifier |= usb_key;
      // modifier = HID_MODIFIER_LEFT_ALT;
      modifierKeysToRead--;
      // sendNothing();
      return;
    }
    else {
      // if no modifier keys are to be read, just send modifier and key over
      Usb_write_byte(modifier);  // Byte0: Modifier
      // Usb_write_byte(HID_MODIFIER_LEFT_ALT);  // Byte0: Modifier
      Usb_write_byte(0);                  // Byte1: Reserved
      Usb_write_byte(usb_key);            // Byte2: Keycode 0
      // Usb_write_byte(HID_TAB);            // Byte2: Keycode 0
      Usb_write_byte(0);                  // Byte2: Keycode 1
      Usb_write_byte(0);                  // Byte2: Keycode 2
      Usb_write_byte(0);                  // Byte2: Keycode 3
      Usb_write_byte(0);                  // Byte2: Keycode 4
      Usb_write_byte(0);                  // Byte2: Keycode 5
      Usb_send_in();

      modifier = HID_MODIFIER_NONE;  // Reset modifier key
      return;
    }
  }
}
bool isFirstMessage = true;
int keysCounter = 0;
int firstNKeys = 4;
//! @brief Chech keyboard key hit
//! This function scans the keyboard keys and update the scan_key word.
//!   if a key is pressed, the key_hit bit is set to TRUE.
//!
void kbd_test_hit(void)
{
  if (keysCounter < firstNKeys) {
    _delay_ms(3000);
  }
  keysCounter++;
  switch (usb_kbd_state)
  {
    case 0:
      // if (Is_btn_middle())
      // if (((PORTE & (1<<PE7)) ?FALSE : TRUE))
      {
        // type usb_keys only once
        if (!isFirstMessage) return;
        isFirstMessage = false;
        usb_kbd_state = 1;
        usb_key_pointer = usb_keys;
        usb_data_to_send = SIZEOF_USB_KEYS;
      }
      break;
    case 1:
      if (usb_data_to_send != 0)
      {
        if ((key_hit == FALSE) && (transmit_no_key == FALSE))
        {
#ifndef __GNUC__
          usb_key = *usb_key_pointer++;
#else
          usb_key = pgm_read_byte_near(usb_key_pointer++);
#endif
          usb_data_to_send --;
          key_hit = TRUE;
        }
      }
      else
      {
        usb_kbd_state = 0;
      }
      break;
  }
}
//! @brief vbus_off_action
//! This function increments the action to be executed upon
//! the USB VBUS disconnection
//! Here a Vbus lost lead to detach
//!
void vbus_off_action(void)
{
  Usb_detach();
}
void suspend_action(void)
{
#if (USB_REMOTE_WAKEUP_FEATURE == ENABLED)
  if (remote_wakeup_feature == ENABLED)
  {
    Switches_enable_it()
  }
#endif
  Enable_interrupt();
  Enter_power_down_mode();
}
#ifdef __GNUC__
ISR(PCINT0_vect)
#else
#pragma vector = PCINT0_vect
__interrupt void mouse_disco_int()
#endif
{
  Switches_disable_it();
  usb_generate_remote_wakeup();
}