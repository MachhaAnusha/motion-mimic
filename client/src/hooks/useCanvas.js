import { useEffect, useRef, useState } from 'react';
import { fabric } from 'fabric';

export const useCanvas = (canvasRef, initialOptions = {}) => {
  const canvas = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (canvasRef.current && !canvas.current) {
      // Initialize Fabric.js canvas
      canvas.current = new fabric.Canvas(canvasRef.current, {
        backgroundColor: '#1a1a1a',
        isDrawingMode: true,
        ...initialOptions,
      });

      // Set up default brush
      canvas.current.freeDrawingBrush.width = 5;
      canvas.current.freeDrawingBrush.color = '#39ff14';

      setIsReady(true);
    }

    return () => {
      if (canvas.current) {
        canvas.current.dispose();
        canvas.current = null;
      }
    };
  }, [canvasRef, initialOptions]);

  const clearCanvas = () => {
    if (canvas.current) {
      canvas.current.clear();
      canvas.current.backgroundColor = '#1a1a1a';
      canvas.current.renderAll();
    }
  };

  const getCanvasData = (options = {}) => {
    if (canvas.current) {
      return canvas.current.toDataURL({
        format: 'png',
        quality: 1,
        ...options,
      });
    }
    return null;
  };

  const setBackgroundImage = (imageUrl, options = {}) => {
    if (canvas.current && imageUrl) {
      fabric.Image.fromURL(imageUrl, (img) => {
        canvas.current.setBackgroundImage(img, canvas.current.renderAll.bind(canvas.current), {
          scaleX: canvas.current.width / img.width,
          scaleY: canvas.current.height / img.height,
          ...options,
        });
      });
    }
  };

  const addText = (text, options = {}) => {
    if (canvas.current && text) {
      const textObject = new fabric.Text(text, {
        left: canvas.current.width / 2,
        top: canvas.current.height / 2,
        originX: 'center',
        originY: 'center',
        fontSize: 48,
        fill: '#39ff14',
        fontFamily: 'Boogaloo, cursive',
        ...options,
      });

      canvas.current.add(textObject);
      canvas.current.setActiveObject(textObject);
      canvas.current.renderAll();

      return textObject;
    }
    return null;
  };

  const setBrushProperties = (properties) => {
    if (canvas.current && canvas.current.freeDrawingBrush) {
      Object.assign(canvas.current.freeDrawingBrush, properties);
    }
  };

  const undo = () => {
    if (canvas.current) {
      const objects = canvas.current.getObjects();
      if (objects.length > 0) {
        canvas.current.remove(objects[objects.length - 1]);
        canvas.current.renderAll();
      }
    }
  };

  const redo = () => {
    // In a real implementation, this would maintain a history stack
    // For now, this is a placeholder
    console.log('Redo functionality would be implemented here');
  };

  return {
    canvas: canvas.current,
    isReady,
    clearCanvas,
    getCanvasData,
    setBackgroundImage,
    addText,
    setBrushProperties,
    undo,
    redo,
  };
};
