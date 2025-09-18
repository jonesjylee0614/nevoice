import { CARD_ELEMENT_KEY } from '../../constants';
import type { EngineInterface, RangeInterface } from '../../types';

class Backspace {
  private engine: EngineInterface;
  constructor(engine: EngineInterface) {
    this.engine = engine;
  }

  trigger(event: any) {
    const { change, node, block, card } = this.engine;
    const range = change.range.get();
    if (!range.collapsed) return;
    const prevNode = range.getPrevNode();
    if (prevNode && node.isBlock(prevNode) && node.isEmptyWithTrim(prevNode)) {
      event.preventDefault();
      const parent = prevNode.parent();
      prevNode.remove();
      if (parent && this.engine.node.isEmpty(parent)) {
        if (parent.isEditable()) {
          this.engine.node.html(parent, '<p><br /></p>');
          range.select(parent, true).shrinkToElementNode().collapse(false);
        } else {
          this.engine.node.html(parent, '<br />');
          range.select(parent, true).collapse(false);
        }
        change.apply(range);
      }
      return false;
    }
    // 光标不在段落开始位置时
    const isCard = Boolean(card.closest(range.startNode));
    if (!isCard && !block.isFirstOffset(range, 'start')) {
      const cloneRange = range.cloneRange().shrinkToElementNode().shrinkToTextNode();
      if (
        cloneRange.startContainer.nodeType === Node.TEXT_NODE &&
        ((rg: RangeInterface) => {
          const { commonAncestorContainer, commonAncestorNode } = rg;
          const commonAncestorParent = commonAncestorNode.parent();
          const commonAncestorAttributes = commonAncestorParent?.attributes();
          if (
            rg.collapsed &&
            rg.startOffset === 1 &&
            rg.startContainer === commonAncestorContainer &&
            commonAncestorContainer.nodeType === Node.TEXT_NODE &&
            (!commonAncestorAttributes || !['left', 'right'].includes(commonAncestorAttributes[CARD_ELEMENT_KEY]))
          ) {
            rg = rg.cloneRange();
            if (
              (commonAncestorContainer.parentNode?.childNodes?.length || 0) <= 1 &&
              commonAncestorContainer.textContent?.length === 1
            ) {
              const { startNode, startOffset } = rg;
              const markNode = startNode.parent();
              // 开始节点在mark标签内
              if (markNode && node.isMark(markNode) && startOffset > 0) {
                const text = startNode.text();
                const leftText = text.substring(startOffset - 1, 1);
                // 不位于零宽字符后，不处理
                if (/^\u200B$/.test(leftText)) {
                  // 选中上一个节点
                  if (startOffset === 1) {
                    const prev = markNode.prev();
                    if (prev && !node.isEmpty(prev)) {
                      const { startNode: sNode, startOffset: offset } = rg
                        .cloneRange()
                        .select(prev, true)
                        .shrinkToTextNode()
                        .collapse(false);
                      rg.setStart(sNode, offset - 1);
                    }
                  } else {
                    rg.setStart(startNode, startOffset - 1);
                  }
                }
              }
              if (rg.collapsed) rg.select(commonAncestorContainer, true);
              change.delete(rg, true);
              change.apply(rg);
              return true;
            }
          }
          return false;
        })(cloneRange)
      ) {
        event.preventDefault();
        event.isDelete = true;
        change.change();
      }
      return;
    }
    const blockNode = block.closest(range.startNode);
    // 在正文里
    if (!isCard && node.isRootBlock(blockNode)) {
      event.preventDefault();
      // 空的节点就清空所有的mark空节点以及inline节点，避免重复的合并到上一级节点上
      if (node.isEmpty(blockNode)) blockNode.html('<br />');
      change.mergeAfterDelete(blockNode);
      change.change(false);
      return false;
    }
    return true;
  }
}
export default Backspace;
