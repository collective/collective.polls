import { createContent } from './content';
import { login } from './login';
import { expect, test } from './test';

test.describe('Example acceptance tests', () => {
  test.describe('Visit a page', () => {
    test('As editor I can edit a Page', async ({ page, request }) => {
      // Given a logged in editor and a page
      await createContent(request, {
        contentType: 'Document',
        contentId: 'document',
        contentTitle: 'Test document',
      });
      await login(page);

      // When the editor opens the page for editing
      await page.goto('/document/edit');

      // Then the toolbar with the save button is shown
      const save = page.locator('#toolbar-save');
      await expect(save).toBeVisible();

      // And saving takes the editor back to the page
      await save.click();
      await expect(page).toHaveURL(/\/document$/);
    });
  });
});
