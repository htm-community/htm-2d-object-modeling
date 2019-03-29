import objects from './objects/*.yml'  // loads all the yaml objects and parses them.
import $ from "jquery"

$(() => {

    const cellSize = 20
    const $container = $('#environments')

    function renderObjectToCanvas(object, $parent) {
        let $title = $('<div>').html(object.name)
        let $canvas = $('<canvas>')

        $parent.append($title)
        $parent.append($canvas)

        const ctx = $canvas[0].getContext('2d')
        $canvas.attr('width', cellSize * object.width)
        $canvas.attr('height', cellSize * object.height)
        ctx.font = cellSize + 'px sans-serif'
        object.features.forEach(feature => {
            ctx.fillText(
                feature.data,
                feature.y * cellSize,
                feature.x * cellSize + cellSize)
        })
    }

    // render all the objects
    Object.values(objects).forEach((value) => {
        renderObjectToCanvas(value, $container)
    })

    // Or render them individually
    // renderObjectToCanvas(objects['a'], $container)

})
